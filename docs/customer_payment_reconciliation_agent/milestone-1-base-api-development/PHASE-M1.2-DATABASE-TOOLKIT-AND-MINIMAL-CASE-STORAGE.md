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

P_bottom_up: about 390 production LOC.
T_bottom_up: about 260 test LOC.

## Execution Plan

### Red

- `test_database_session_uses_settings_database_url`
  - Summary: Verifies the session factory uses `Settings.database_url` and does
    not require Redis, Ollama, worker, tenant, or auth settings.
  - Mocks: A test `Settings` object with the local PostgreSQL URL.
  - Assertions: Engine/session creation succeeds and uses the configured URL.

- `test_reconciliation_case_migration_creates_table`
  - Summary: Verifies Alembic upgrades create `reconciliation_cases` with the
    Base API storage columns from [../MODELS.md](../MODELS.md).
  - Mocks: A disposable test database/schema when available.
  - Assertions: The table, status index, created timestamp index, and JSON
    snapshot columns exist after upgrade.

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
- Add database package files under `backend/app/db/`.
- Add SQLAlchemy model and repository under
  `backend/app/features/reconciliation/`.
- Add Alembic config and first migration under `backend/migrations/`.

Required signatures:

```python
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

    What: Opens, yields, and closes a SQLAlchemy session.
    Why: Later API routes need a FastAPI dependency with predictable cleanup.

    Yields:
        Session: Active database session.

    States / Side Effects:
        Opens and closes a database connection.
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

Settings and configuration: `DATABASE_URL` only.

Environment variables:

```bash
DATABASE_URL=postgresql://reconai:reconai@localhost:5432/reconai
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
| 9 | Rollback addresses in-flight tenant data | Addressed | Downgrade drops only the new empty table before API writes exist. |
| 10 | Kill switch drill without redeploy | N/A | No runtime feature is exposed. |

## Summary of Changes

- [../../../backend/pyproject.toml](../../../backend/pyproject.toml) (modify): Adds DB and migration dependencies for L1.
- `backend/alembic.ini` (new): Adds Alembic entrypoint for L2.
- `backend/migrations/env.py` (new): Wires migrations to app metadata for L2.
- `backend/migrations/versions/0001_reconciliation_cases.py` (new): Creates the Base API case table for L3.
- `backend/app/db/session.py` (new): Adds engine/session helpers for L4.
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
| L1 | inherited | [../PLAN.md](../PLAN.md#m12-database-toolkit-and-minimal-case-storage) | -- | resolved |
| L2 | phase-local | Alembic env required for migrations | -- | phase-local |
| L3 | inherited | [../MODELS.md](../MODELS.md#base-api-persistence-model) | -- | resolved |
| L4 | phase-local | DB session helpers needed before repository/API | -- | phase-local |
| L5 | inherited | [../DEFINITIONS.md](../DEFINITIONS.md#repository-port) | -- | resolved |
| L6 | inherited | [../TESTING.md](../TESTING.md#milestone-1-base-api-tests) | -- | resolved |
| L7 | assumption | Current backend has no Alembic/ORM | -- | verified in code |

</details>
