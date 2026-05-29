from collections.abc import Iterator
from importlib import import_module
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import get_engine

LOCAL_DATABASE_URL = "postgresql+psycopg://reconai:reconai@localhost:5432/reconai"


@pytest.fixture
def migrated_connection() -> Iterator[sa.Connection]:
    """Create an isolated migrated schema for dependency composition tests."""
    engine = get_engine(LOCAL_DATABASE_URL)
    schema_name = f"test_recon_{uuid4().hex}"

    try:
        with engine.connect() as connection:
            connection.execute(sa.schema.CreateSchema(schema_name))
            connection.execute(text(f'SET search_path TO "{schema_name}"'))
            alembic_config = Config("alembic.ini")
            alembic_config.attributes["connection"] = connection
            command.upgrade(alembic_config, "head")
            yield connection
    except OperationalError as exc:
        pytest.fail(f"Local PostgreSQL is required for M1.4 tests: {exc}")
    finally:
        with engine.begin() as cleanup_connection:
            cleanup_connection.execute(
                text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
            )
        engine.dispose()


def test_reconciliation_layers_import_from_final_paths() -> None:
    """Verifies the final M1.4 reconciliation layer import paths."""
    module_names = [
        "app.domain.reconciliation.contracts",
        "app.domain.reconciliation.decisions",
        "app.schemas.reconciliation",
        "app.db.models.reconciliation",
        "app.repositories.reconciliation",
        "app.services.reconciliation",
        "app.dependencies",
        "app.routers",
    ]

    modules = {name: import_module(name) for name in module_names}

    assert hasattr(
        modules["app.domain.reconciliation.contracts"],
        "ReconciliationStatus",
    )
    assert hasattr(
        modules["app.domain.reconciliation.decisions"],
        "decide_base_reconciliation",
    )
    assert hasattr(
        modules["app.schemas.reconciliation"],
        "ReconciliationCaseCreateRequestV1",
    )
    assert hasattr(
        modules["app.db.models.reconciliation"],
        "BaseReconciliationCaseModel",
    )
    assert hasattr(
        modules["app.repositories.reconciliation"],
        "BaseReconciliationCaseRepository",
    )
    assert hasattr(
        modules["app.services.reconciliation"],
        "BaseReconciliationCaseService",
    )
    assert hasattr(modules["app.dependencies"], "get_reconciliation_case_service")


def test_reconciliation_service_dependency_composes_service(
    migrated_connection: sa.Connection,
) -> None:
    """Verifies M1.4 dependency composition wires repository and service."""
    from app.dependencies import (
        get_reconciliation_case_repository,
        get_reconciliation_case_service,
    )
    from app.services.reconciliation import BaseReconciliationCaseService

    session = Session(migrated_connection, expire_on_commit=False)
    repository = get_reconciliation_case_repository(session)
    settings = Settings(
        DATABASE_URL=LOCAL_DATABASE_URL,
        EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD=0.80,
    )

    service = get_reconciliation_case_service(repository, settings)
    created = service.create_case(_valid_reconciliation_request())
    session.commit()

    assert isinstance(service, BaseReconciliationCaseService)
    assert service.get_case(created.id) == created


def _valid_reconciliation_request():
    from app.schemas.reconciliation import ReconciliationCaseCreateRequestV1

    return ReconciliationCaseCreateRequestV1.model_validate(
        {
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
    )
