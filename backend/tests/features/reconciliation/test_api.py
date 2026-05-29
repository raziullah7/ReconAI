from collections.abc import Callable, Iterator
from dataclasses import dataclass
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import get_engine
from app.dependencies import get_reconciliation_case_service
from app.main import create_app
from app.repositories.reconciliation import BaseReconciliationCaseRepository
from app.services.reconciliation import BaseReconciliationCaseService

LOCAL_DATABASE_URL = "postgresql+psycopg://reconai:reconai@localhost:5432/reconai"


@dataclass(frozen=True, slots=True)
class ApiClientContext:
    """Hold the API client and dependency-call probe for route tests."""

    client: TestClient
    dependency_calls: Callable[[], int]


@pytest.fixture
def migrated_connection() -> Iterator[sa.Connection]:
    """Create an isolated PostgreSQL schema migrated by Alembic.

    Summary:
        Applies the phase migration into a disposable schema for API tests.
    Mocks:
        None. The test fails fast when local PostgreSQL is unavailable.
    Assertions:
        Tests using this fixture exercise the API against migrated storage.
    """
    engine = get_engine(LOCAL_DATABASE_URL)
    schema_name = f"test_recon_api_{uuid4().hex}"

    try:
        with engine.connect() as connection:
            connection.execute(sa.schema.CreateSchema(schema_name))
            connection.execute(text(f'SET search_path TO "{schema_name}"'))
            alembic_config = Config("alembic.ini")
            alembic_config.attributes["connection"] = connection
            command.upgrade(alembic_config, "head")
            yield connection
    except OperationalError as exc:
        pytest.fail(f"Local PostgreSQL is required for M1.5 API tests: {exc}")
    finally:
        with engine.begin() as cleanup_connection:
            cleanup_connection.execute(
                text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
            )
        engine.dispose()


@pytest.fixture
def api_client(migrated_connection: sa.Connection) -> Iterator[ApiClientContext]:
    """Create a TestClient whose service dependency uses migrated storage.

    Summary:
        Overrides the public service dependency with a session-backed service.
    Mocks:
        FastAPI dependency override for `get_reconciliation_case_service`.
    Assertions:
        Tests can prove routes use dependency injection instead of constructing
        services inline.
    """
    session = Session(migrated_connection, expire_on_commit=False)
    settings = Settings(
        DATABASE_URL=LOCAL_DATABASE_URL,
        EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD=0.80,
    )
    application = create_app(settings)
    dependency_call_count = 0

    def build_service() -> BaseReconciliationCaseService:
        nonlocal dependency_call_count
        dependency_call_count += 1
        return BaseReconciliationCaseService(
            BaseReconciliationCaseRepository(session),
            settings.extraction_review_confidence_threshold,
        )

    application.dependency_overrides[get_reconciliation_case_service] = build_service

    with TestClient(application) as client:
        client.headers.update({"X-Request-ID": "test-request-id"})
        yield ApiClientContext(client, lambda: dependency_call_count)

    session.close()


def test_post_reconciliation_case_persists_and_returns_decision(
    api_client: ApiClientContext,
) -> None:
    """Verifies POST creates a stored reconciliation case through the service.

    Summary:
        Posts a valid create request and expects a stored case response.
    Mocks:
        FastAPI TestClient and a database-backed service dependency override.
    Assertions:
        Status is 201, response includes stored snapshots, computed decision,
        timestamps, and the route uses `get_reconciliation_case_service`.
    """
    response = api_client.client.post("/v1/reconciliation-cases", json=_valid_payload())

    body = response.json()

    assert response.status_code == 201
    assert body["id"]
    assert body["external_reference"] == "CALL-001"
    assert body["customer_reference"] == "CUST-001"
    assert body["extraction"]["agreed_amount_minor"] == 250000
    assert body["actual_payment"]["reference"] == "TXN-001"
    assert body["decision"]["status"] == "RECONCILED"
    assert body["decision"]["difference_minor"] == 0
    assert body["created_at"]
    assert body["updated_at"]
    assert api_client.dependency_calls() == 1


def test_get_reconciliation_cases_returns_summaries(
    api_client: ApiClientContext,
) -> None:
    """Verifies GET collection returns newest-first stored case summaries.

    Summary:
        Lists stored cases with `limit` and `offset`.
    Mocks:
        FastAPI TestClient and seeded rows created through POST.
    Assertions:
        Status is 200, newest-first items are returned, and detail-only
        snapshots are not included in summaries.
    """
    first = api_client.client.post(
        "/v1/reconciliation-cases",
        json=_valid_payload(external_reference="CALL-001"),
    ).json()
    second = api_client.client.post(
        "/v1/reconciliation-cases",
        json=_valid_payload(external_reference="CALL-002"),
    ).json()

    response = api_client.client.get(
        "/v1/reconciliation-cases",
        params={"limit": 1},
    )
    offset_response = api_client.client.get(
        "/v1/reconciliation-cases",
        params={"limit": 1, "offset": 1},
    )

    body = response.json()
    offset_body = offset_response.json()

    assert response.status_code == 200
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == second["id"]
    assert body["items"][0]["external_reference"] == "CALL-002"
    assert "extraction" not in body["items"][0]
    assert "actual_payment" not in body["items"][0]
    assert offset_response.status_code == 200
    assert offset_body["items"][0]["id"] == first["id"]
    assert first["id"] != second["id"]


def test_get_reconciliation_case_returns_detail_or_not_found(
    api_client: ApiClientContext,
) -> None:
    """Verifies GET detail returns stored cases and not-found envelopes.

    Summary:
        Fetches one stored case and verifies unknown IDs use the error envelope.
    Mocks:
        FastAPI TestClient and a row created through POST.
    Assertions:
        Existing ID returns 200 detail; unknown ID returns 404 with the
        canonical `{ "error": { "code", "message", "request_id" } }` shape.
    """
    created = api_client.client.post(
        "/v1/reconciliation-cases",
        json=_valid_payload(),
    ).json()

    found = api_client.client.get(f"/v1/reconciliation-cases/{created['id']}")
    missing = api_client.client.get(f"/v1/reconciliation-cases/{uuid4()}")

    assert found.status_code == 200
    assert found.json()["id"] == created["id"]
    assert found.json()["extraction"]["schema_version"] == "agreement_extraction.v1"
    assert missing.status_code == 404
    assert missing.json() == {
        "error": {
            "code": "NotFound",
            "message": "Reconciliation case was not found.",
            "request_id": "test-request-id",
        }
    }


def test_invalid_reconciliation_case_uses_error_envelope(
    api_client: ApiClientContext,
) -> None:
    """Verifies request and service validation use canonical errors.

    Summary:
        Posts invalid Pydantic data and valid-shape data rejected by service
        validation, then expects the canonical error shape.
    Mocks:
        FastAPI TestClient.
    Assertions:
        Pydantic validation returns 422, service validation returns 400,
        `error.code` is `ValidationFailed`, and `error.request_id` is present.
    """
    invalid_schema = api_client.client.post(
        "/v1/reconciliation-cases",
        json=_valid_payload(extraction={"schema_version": "wrong"}),
    )
    service_rejected = api_client.client.post(
        "/v1/reconciliation-cases",
        json=_valid_payload(
            extraction={
                "schema_version": "agreement_extraction.v1",
                "agreed_amount_minor": 250000,
                "currency": "PKR",
                "payment_type": "FULL_PAYMENT",
                "due_date": "2026-06-10",
                "is_final_amount": True,
                "evidence_text": None,
                "confidence": 0.50,
                "needs_human_review": True,
            },
        ),
    )

    assert invalid_schema.status_code == 422
    assert invalid_schema.json()["error"]["code"] == "ValidationFailed"
    assert invalid_schema.json()["error"]["message"]
    assert invalid_schema.json()["error"]["request_id"] == "test-request-id"
    assert service_rejected.status_code == 400
    assert service_rejected.json()["error"]["code"] == "ValidationFailed"
    assert service_rejected.json()["error"]["message"]
    assert service_rejected.json()["error"]["request_id"] == "test-request-id"


def _valid_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "external_reference": "CALL-001",
        "customer_reference": "CUST-001",
        "source_text": "Customer agreed to pay PKR 2,500.",
        "extraction": {
            "schema_version": "agreement_extraction.v1",
            "agreed_amount_minor": 250000,
            "currency": "PKR",
            "payment_type": "FULL_PAYMENT",
            "due_date": "2026-06-10",
            "is_final_amount": True,
            "evidence_text": "Customer agreed to pay PKR 2,500 by June 10.",
            "confidence": 0.92,
            "needs_human_review": False,
            "model_name": "mock-extractor",
            "raw_llm_output": {"source": "fixture"},
        },
        "actual_payment": {
            "paid_amount_minor": 250000,
            "currency": "PKR",
            "payment_date": "2026-06-09",
            "reference": "TXN-001",
            "payment_method": "bank_transfer",
        },
    }
    payload.update(overrides)
    return payload
