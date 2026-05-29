from collections.abc import Iterator
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import get_engine
from app.domain.reconciliation.contracts import (
    ReconciliationCaseCreateV1,
    ReconciliationDecisionV1,
    ReconciliationStatus,
)
from app.repositories.reconciliation import BaseReconciliationCaseRepository

LOCAL_DATABASE_URL = "postgresql+psycopg://reconai:reconai@localhost:5432/reconai"


@pytest.fixture
def migrated_connection() -> Iterator[sa.Connection]:
    """Create an isolated PostgreSQL schema migrated by Alembic.

    Summary:
        Applies the phase migration into a disposable schema.
    Mocks:
        None. The test fails fast when local PostgreSQL is unavailable.
    Assertions:
        Tests using this fixture inspect the migrated schema or exercise the
        repository against it.
    """
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
        pytest.fail(f"Local PostgreSQL is required for M1.2 tests: {exc}")
    finally:
        with engine.begin() as cleanup_connection:
            cleanup_connection.execute(
                text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
            )
        engine.dispose()


def test_database_engine_uses_settings_database_url() -> None:
    """Verifies the DB engine uses the settings database URL.

    Summary:
        Creates an engine from a validated settings object.
    Mocks:
        A test `Settings` object with the explicit psycopg SQLAlchemy URL.
    Assertions:
        The engine preserves the configured URL and uses the psycopg driver.
    """
    settings = Settings(DATABASE_URL=LOCAL_DATABASE_URL)

    engine = get_engine(settings.database_url)

    assert engine.url.drivername == "postgresql+psycopg"
    assert engine.url.database == "reconai"

    engine.dispose()


def test_reconciliation_case_migration_creates_table(
    migrated_connection: sa.Connection,
) -> None:
    """Verifies the M1.2 migration creates the Base API table.

    Summary:
        Inspects the migrated `reconciliation_cases` schema.
    Mocks:
        A disposable PostgreSQL schema with isolated Alembic version state.
    Assertions:
        Required columns, indexes, and constraints exist, and no tenant column
        is introduced.
    """
    inspector = inspect(migrated_connection)

    columns = {
        column["name"]
        for column in inspector.get_columns("reconciliation_cases")
    }
    indexes = {
        index["name"]
        for index in inspector.get_indexes("reconciliation_cases")
    }
    checks = {
        constraint["name"]: constraint["sqltext"]
        for constraint in inspector.get_check_constraints("reconciliation_cases")
    }

    assert columns == {
        "id",
        "external_reference",
        "customer_reference",
        "source_text",
        "extraction_snapshot_json",
        "actual_payment_snapshot_json",
        "agreed_amount_minor",
        "paid_amount_minor",
        "difference_minor",
        "currency",
        "status",
        "reason",
        "needs_human_review",
        "confidence",
        "version",
        "created_at",
        "updated_at",
    }
    assert "tenant_id" not in columns
    assert {"idx_base_cases_created", "idx_base_cases_status"} <= indexes
    assert "ck_reconciliation_cases_status" in checks
    assert "ck_reconciliation_cases_confidence" in checks
    assert "ck_reconciliation_cases_difference" in checks


def test_reconciliation_case_repository_create_list_get_round_trip(
    migrated_connection: sa.Connection,
) -> None:
    """Verifies repository create, list, and get behavior.

    Summary:
        Stores two cases and reads them back through repository methods.
    Mocks:
        None. Uses the migrated PostgreSQL schema from the fixture.
    Assertions:
        Snapshots and computed fields round-trip, unknown IDs return None, and
        list order is newest-first.
    """
    session = Session(migrated_connection, expire_on_commit=False)
    repository = BaseReconciliationCaseRepository(session)
    create_input = ReconciliationCaseCreateV1(
        external_reference="CALL-001",
        customer_reference="CUST-001",
        source_text="Customer agreed to pay PKR 2,500.",
        extraction_snapshot={
            "schema_version": "agreement_extraction.v1",
            "agreed_amount_minor": 250000,
            "currency": "PKR",
            "confidence": 0.92,
            "needs_human_review": False,
        },
        actual_payment_snapshot={
            "paid_amount_minor": 250000,
            "currency": "PKR",
            "reference": "TXN-001",
        },
    )
    decision = ReconciliationDecisionV1(
        status=ReconciliationStatus.RECONCILED,
        agreed_amount_minor=250000,
        paid_amount_minor=250000,
        difference_minor=0,
        currency="PKR",
        reason="Payment matched the agreed amount.",
        needs_human_review=False,
        confidence=0.92,
    )

    first_case = repository.create(create_input, decision)
    session.commit()
    second_case = repository.create(create_input, decision)
    session.commit()

    listed_cases = repository.list(status=None, limit=10, offset=0)
    fetched_case = repository.get(first_case.id)
    missing_case = repository.get(uuid4())

    assert listed_cases[0].id == second_case.id
    assert fetched_case == first_case
    assert missing_case is None
    assert first_case.extraction_snapshot["schema_version"] == "agreement_extraction.v1"
    assert first_case.actual_payment_snapshot is not None
    assert first_case.actual_payment_snapshot["reference"] == "TXN-001"
    assert first_case.difference_minor == 0
    assert first_case.status is ReconciliationStatus.RECONCILED
