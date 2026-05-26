# PHASE-M1.2-DATABASE-TOOLKIT-AND-MINIMAL-CASE-STORAGE.md

## Executive Summary

This phase adds the smallest database foundation needed to persist Base API
reconciliation cases. It introduces SQLAlchemy 2.x, Alembic, psycopg, a database
session boundary, the `reconciliation_cases` table, and repository
`create/list/get` behavior.

Expected outcome: the backend can migrate PostgreSQL and round-trip stored case
records without exposing HTTP endpoints or reconciliation rules yet.

Assumptions:

- PostgreSQL continues to run from the existing DB-only Compose service.
- The current backend has no Alembic, ORM model, DB session, or repository.
- Milestone 1 remains non-tenantized.

P_bottom_up: about 470 production LOC.
T_bottom_up: about 330 test LOC.

## Execution Plan

### Red

- `test_database_engine_uses_settings_database_url`
  - Summary: Verifies the engine helper accepts `Settings.database_url` using
    the explicit psycopg SQLAlchemy URL and does not require Redis, Ollama,
    worker, tenant, or auth settings.
  - Mocks: A test `Settings` object with
    `postgresql+psycopg://reconai:reconai@localhost:5432/reconai`.
  - Assertions: Engine creation succeeds, the dialect driver is `psycopg`, and
    the configured URL is preserved.

- `test_reconciliation_case_migration_creates_table`
  - Summary: Verifies Alembic upgrades create `reconciliation_cases` with the
    Base API storage columns from [../MODELS.md](../MODELS.md).
  - Mocks: A disposable PostgreSQL database or schema with isolated Alembic
    version state; the test must fail fast when PostgreSQL is unavailable
    instead of silently falling back to SQLite.
  - Assertions: Every Base API column exists using snake_case names, the status
    and created timestamp indexes exist, JSON snapshot columns exist, there is
    no tenant column, status values are constrained, confidence is constrained
    to 0..1, and `difference_minor` equals `paid_amount_minor -
    agreed_amount_minor` when both amounts exist.

- `test_reconciliation_case_repository_create_list_get_round_trip`
  - Summary: Verifies the repository can create one case, list newest-first, and
    fetch by ID.
  - Mocks: None when running against PostgreSQL; use a transaction fixture for
    cleanup.
  - Assertions: Snapshots are stored, computed amount fields are preserved,
    unknown IDs return `None`, and list order is newest-first.

### Green

- Add dependencies in [../../../backend/pyproject.toml](../../../backend/pyproject.toml):
  `sqlalchemy>=2.0`, `alembic>=1.17`, and `psycopg[binary]>=3.2`.
- Update local database URL examples to use the psycopg 3 SQLAlchemy dialect:
  `postgresql+psycopg://reconai:reconai@localhost:5432/reconai`.
- Add database package files under `backend/app/db/`.
- Add SQLAlchemy model and repository under
  `backend/app/features/reconciliation/`.
- Add Alembic config and first migration under `backend/migrations/`.
- Add minimal typed persistence contracts under
  `backend/app/features/reconciliation/contracts.py`.

Database schema requirements:

- Table name: `reconciliation_cases`.
- Columns: `id`, `external_reference`, `customer_reference`, `source_text`,
  `extraction_snapshot_json`, `actual_payment_snapshot_json`,
  `agreed_amount_minor`, `paid_amount_minor`, `difference_minor`, `currency`,
  `status`, `reason`, `needs_human_review`, `confidence`, `version`,
  `created_at`, and `updated_at`.
- Indexes: `idx_base_cases_created` on `created_at` and
  `idx_base_cases_status` on `status`.
- Constraints: no tenant column; `confidence` is between 0 and 1; `status` is
  limited to `RECONCILED`, `UNDERPAID`, `OVERPAID`, `PARTIAL_PAYMENT`,
  `PAYMENT_NOT_FOUND`, `NEEDS_REVIEW`, and `FAILED`; `difference_minor` equals
  `paid_amount_minor - agreed_amount_minor` when both amount columns exist.

Required signatures:

```python
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Mapping
from uuid import UUID


class ReconciliationStatus(StrEnum):
    """Status values persisted by the Base API repository."""

    RECONCILED = "RECONCILED"
    UNDERPAID = "UNDERPAID"
    OVERPAID = "OVERPAID"
    PARTIAL_PAYMENT = "PARTIAL_PAYMENT"
    PAYMENT_NOT_FOUND = "PAYMENT_NOT_FOUND"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class ReconciliationCaseCreateV1:
    """Carry snapshots and optional references into persistence."""

    external_reference: str | None
    customer_reference: str | None
    source_text: str | None
    extraction_snapshot: Mapping[str, object]
    actual_payment_snapshot: Mapping[str, object] | None


@dataclass(frozen=True, slots=True)
class ReconciliationDecisionV1:
    """Carry computed decision fields into persistence."""

    status: ReconciliationStatus
    agreed_amount_minor: int | None
    paid_amount_minor: int | None
    difference_minor: int | None
    currency: str | None
    reason: str
    needs_human_review: bool
    confidence: float


@dataclass(frozen=True, slots=True)
class BaseReconciliationCase:
    """Projection returned by the Base API repository."""

    id: UUID
    external_reference: str | None
    customer_reference: str | None
    source_text: str | None
    extraction_snapshot: Mapping[str, object]
    actual_payment_snapshot: Mapping[str, object] | None
    agreed_amount_minor: int | None
    paid_amount_minor: int | None
    difference_minor: int | None
    currency: str | None
    status: ReconciliationStatus
    reason: str
    needs_human_review: bool
    confidence: float
    version: int
    created_at: datetime
    updated_at: datetime


def get_engine(database_url: str) -> Engine:
    """Create the SQLAlchemy engine for local PostgreSQL access.

    What: Builds the synchronous engine used by migrations, tests, and
        repository sessions.
    Why: Milestone 1 needs one explicit DB boundary before persistence code can
        be tested.

    Args:
        database_url: PostgreSQL connection URL from validated settings.

    Returns:
        Engine: Configured SQLAlchemy engine.
    """


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create the session factory used by repositories.

    What: Binds SQLAlchemy sessions to the configured engine.
    Why: Repositories need injected sessions instead of reading global state.

    Args:
        engine: SQLAlchemy engine created from settings.

    Returns:
        sessionmaker[Session]: Factory that creates synchronous sessions.
    """


def get_session() -> Iterator[Session]:
    """Yield one request-scoped database session.

    What: Loads settings, creates or reuses the cached engine/session factory,
        then opens, yields, commits, rolls back on error, and closes one
        SQLAlchemy session.
    Why: Later API routes need a FastAPI dependency with predictable cleanup.

    Yields:
        Session: Active database session.

    States / Side Effects:
        Opens and closes a database connection.
    """


class BaseReconciliationCaseRepository:
    """Persist and read Base API reconciliation cases."""

    def __init__(self, session: Session) -> None:
        """Store the injected SQLAlchemy session used by repository methods."""

    def create(
        self,
        input: ReconciliationCaseCreateV1,
        decision: ReconciliationDecisionV1,
    ) -> BaseReconciliationCase:
        """Persist one case from snapshots and a backend-owned decision.

        What: Inserts one `reconciliation_cases` row, flushes generated
            identifiers and timestamps, and maps the row back to a projection.
        Why: Later service and API phases need persistence that does not own
            validation or decision logic.

        Args:
            input: Original request snapshots and optional references.
            decision: Backend-owned reconciliation outcome to store.

        Returns:
            BaseReconciliationCase: Stored case projection.

        States / Side Effects:
            Adds and flushes a SQLAlchemy model in the injected session.
        """

    def list(
        self,
        status: ReconciliationStatus | None,
        limit: int,
        offset: int,
    ) -> list[BaseReconciliationCase]:
        """Return stored cases in newest-first order.

        What: Reads stored cases, optionally filters by status, and applies
            limit/offset pagination.
        Why: M1.4 list endpoints need a repository query that remains local
            and non-tenantized for Milestone 1.

        Args:
            status: Optional reconciliation status filter.
            limit: Maximum number of cases to return.
            offset: Number of newest-first rows to skip.

        Returns:
            list[BaseReconciliationCase]: Matching stored case projections.
        """

    def get(self, case_id: UUID) -> BaseReconciliationCase | None:
        """Return one stored case by ID or None when it does not exist.

        What: Loads a single case by primary key and maps it to the repository
            projection when present.
        Why: M1.4 detail endpoints need a not-found-safe repository lookup.

        Args:
            case_id: Primary key of the case to fetch.

        Returns:
            BaseReconciliationCase | None: Stored case projection, or None.
        """
```

Repository pseudo code:

```text
BaseReconciliationCaseRepository.create(input, decision):
    build BaseReconciliationCaseModel from snapshots and computed fields
    add model to injected session
    flush so id and timestamps are available
    return mapped domain projection

BaseReconciliationCaseRepository.list(status, limit, offset):
    select rows ordered by created_at desc
    apply status filter when provided
    apply limit and offset
    map rows to BaseReconciliationCase projections

BaseReconciliationCaseRepository.get(case_id):
    select by primary key
    return mapped projection or None
```

### Refactor

- Keep repository mapping helpers private to the repository module.
- Keep migration and model column names aligned with [../MODELS.md](../MODELS.md).
- Do not add API routers, validation rules, auth, tenants, or worker code.

## Setup and Testing in Local Dev

Settings and configuration: `DATABASE_URL` only. Use the explicit
`postgresql+psycopg://` SQLAlchemy URL because this phase installs psycopg 3.

Environment variables:

```bash
DATABASE_URL=postgresql+psycopg://reconai:reconai@localhost:5432/reconai
```

Local commands:

```bash
docker compose up -d postgres
cd backend
uv sync
uv run alembic upgrade head
uv run python -m pytest tests/test_config.py tests/test_health.py tests/features/reconciliation/test_repository.py
uv run mypy app
uv run ruff check .
```

Multi-tenant coverage: N/A because Milestone 1 deliberately has no tenant
column. Tests should assert no tenant fixture is required.

Tenant-aware test cases: N/A because tenant behavior is deferred.

Expected outcome: migration succeeds, repository tests pass, health/config tests
still pass.

## Rollout Plan and Testing in QA and Staging

QA/staging steps:

1. Set `DATABASE_URL` for the environment.
2. Run `uv run alembic upgrade head`.
3. Run repository and migration tests against the QA/staging database.
4. Confirm `GET /health` still returns the Phase 1 response.

Expected outcome: schema exists and no API behavior is exposed yet.

Configuration changes: `DATABASE_URL` remains the only runtime URL.

Data setup or migration steps: apply the first Alembic migration.

## Rollout to Production

Production steps:

1. Back up the empty or local-development database before first migration.
2. Run `uv run alembic upgrade head`.
3. Confirm the `reconciliation_cases` table and indexes exist.
4. Confirm existing `/health` behavior is unchanged.
5. Roll back with `uv run alembic downgrade base` only before any Base API
   writes exist, or restore the pre-migration backup if data was written.

Expected outcome: production has the minimal table ready for later phases.

Configuration changes: none beyond existing `DATABASE_URL`.

Data setup or migration steps: first migration only.

## SaaS Pre-Flight Disposition

| # | Item | Disposition | Evidence / Steps |
|---|------|-------------|------------------|
| 1 | Local dev multi-tenant coverage | N/A | Milestone 1 is non-tenantized; repository tests assert no tenant fixture. |
| 2 | Tenant-aware test cases | N/A | Tenant context is deferred. |
| 3 | Per-environment feature flag state | N/A | No feature flag ships in this phase. |
| 4 | Per-tenant production canary | N/A | No tenant model exists. |
| 5 | Observability verification | N/A | No request/runtime behavior changes beyond DB migration. |
| 6 | Audit log verification | N/A | Audit logging is deferred. |
| 7 | Rate limit / quota verification | N/A | No API endpoint ships. |
| 8 | Webhook delivery verification | N/A | Webhooks are not in scope. |
| 9 | Rollback addresses in-flight tenant data | Addressed | Downgrade is allowed only before Base API writes exist; otherwise restore the pre-migration backup. |
| 10 | Kill switch drill without redeploy | N/A | No runtime feature is exposed. |

## Summary of Changes

- [../../../.env.example](../../../.env.example) (modify): Uses the explicit psycopg SQLAlchemy URL for L1.
- [../../../backend/README.md](../../../backend/README.md) (modify): Updates local DB commands to the psycopg URL for L1.
- [../CONFIG.md](../CONFIG.md) (modify): Owns the explicit psycopg SQLAlchemy URL for L1.
- [../../../backend/pyproject.toml](../../../backend/pyproject.toml) (modify): Adds DB and migration dependencies for L1.
- `backend/alembic.ini` (new): Adds Alembic entrypoint for L2.
- `backend/migrations/env.py` (new): Wires migrations to app metadata for L2.
- `backend/migrations/versions/0001_reconciliation_cases.py` (new): Creates the Base API case table for L3.
- `backend/app/db/session.py` (new): Adds engine/session helpers for L4.
- `backend/app/features/reconciliation/contracts.py` (new): Adds typed persistence DTOs and status values for L5.
- `backend/app/features/reconciliation/models.py` (new): Adds the SQLAlchemy model for L5.
- `backend/app/features/reconciliation/repository.py` (new): Adds create/list/get storage behavior for L6.
- `backend/tests/features/reconciliation/test_repository.py` (new): Adds repository and migration coverage for L7.

## Code Generation Instructions

See `planning-conventions` -> Code Generation Instructions. Lint, types,
docstrings, commits, and change-summary rules apply unchanged.

<details>
<summary>Coverage Ledger</summary>

| ID | Category | Source | Pushed to (owner file) | Status |
|----|----------|--------|------------------------|--------|
| L1 | inherited | [../PLAN.md](../PLAN.md#milestone-1-base-api-development) M1.2 table row | -- | resolved |
| L2 | phase-local | Alembic env required for migrations | -- | phase-local |
| L3 | inherited | [../MODELS.md](../MODELS.md#base-api-persistence-model) | -- | resolved |
| L4 | phase-local | DB session helpers needed before repository/API | -- | phase-local |
| L5 | inherited | [../DEFINITIONS.md](../DEFINITIONS.md#repository-port) | -- | resolved |
| L6 | inherited | [../TESTING.md](../TESTING.md#milestone-1-base-api-tests) | -- | resolved |
| L7 | assumption | Current backend has no Alembic/ORM | -- | verified in code |
| L8 | assumption | PostgreSQL remains the only Compose service | -- | verified in code |
| L9 | assumption | Milestone 1 remains non-tenantized | -- | resolved |

</details>
