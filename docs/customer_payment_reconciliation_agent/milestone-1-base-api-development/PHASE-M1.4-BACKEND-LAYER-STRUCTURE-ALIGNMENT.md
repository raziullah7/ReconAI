# PHASE-M1.4-BACKEND-LAYER-STRUCTURE-ALIGNMENT.md

## Executive Summary

This phase aligns the existing Milestone 1 backend code with the lightweight
FastAPI layer structure described in [../ARCH.md](../ARCH.md#backend-layer-map)
and [../DEFINITIONS.md](../DEFINITIONS.md#backend-layer-responsibilities),
with component location owned by [../SPEC.md](../SPEC.md#component-matching-and-reconciliation).
It is a behavior-preserving refactor before HTTP endpoints ship: reconciliation domain
logic, schemas, repository, service, database model, and dependency composition
move into top-level layer packages.

Expected outcome: M1.2 and M1.3 behavior still passes, and M1.5 can add routes
against stable `app.routers`, `app.services`, `app.repositories`, `app.domain`,
`app.schemas`, `app.db.models`, and `app.dependencies` boundaries. M1.4 adds
the router package boundary only; route handler modules remain M1.5 work.

Assumptions:

- M1.2 has delivered database settings, session tooling, Alembic metadata, the
  reconciliation table migration, and a session-backed repository.
- M1.3 has delivered validation, deterministic decision logic, and the
  reconciliation service.
- Milestone 1 remains local, unauthenticated, non-tenantized, and no-LLM.
- The studied workforce-one codebase is a reference for layer separation, not a
  source to copy auth, tenant, task, Neo4j, Redis, or observability systems.

P_bottom_up: about 120 production LOC for import edits, dependency wiring, and
package initializers, plus repository-recognized file moves.
T_bottom_up: about 70 test LOC for focused structure and dependency-composition
coverage, plus import updates in existing tests.

Sizing rationale:

| Artifact | Estimate | Notes |
| --- | ---: | --- |
| Dependency helpers | 35 production LOC | Two provider functions with docstrings. |
| Package initializers | 20 production LOC | Layer package boundaries, including empty router package. |
| Import updates | 45 production LOC | Existing modules, tests, and Alembic metadata path. |
| Structure tests | 35 test LOC | Final-path imports and router package boundary. |
| Dependency-composition test | 35 test LOC | Direct provider calls plus existing service flow. |

This is a scaffold/refactor phase under the learning-friendly 50-200 production
LOC guidance; repository-recognized file moves are treated as organization churn,
not new behavior.

## Execution Plan

### Red

- `test_reconciliation_layers_import_from_final_paths`
  - Summary: Imports the reconciliation domain, schema, repository, service,
    database model, and router package through the new top-level layer paths.
  - Mocks: None.
  - Assertions: Imports succeed from final paths; old `app.features` paths are
    not required by tests; no route handler module is required until M1.5.

- `test_reconciliation_service_dependency_composes_service`
  - Summary: Verifies dependency composition creates a service from settings,
    a SQLAlchemy session-backed repository, and the configured confidence
    threshold.
  - Mocks: Use the existing database/session fixture pattern from M1.2 when a
    real session is needed; do not add a new database service.
  - Assertions: Directly call provider functions with explicit `session`,
    `repository`, and `settings` fixtures; confirm the returned service can run
    an existing M1.3 create/list/get flow through the composed repository.

- Existing M1.2 and M1.3 tests
  - Summary: Keep persistence, validation, decision, and service behavior green
    after import-path changes.
  - Mocks: Existing fixtures only.
  - Assertions: No behavior, schema, migration, or decision output changes.

### Green

- Move reconciliation domain contracts and pure decision logic into
  `backend/app/domain/reconciliation/`.
- Move Pydantic request/response models into
  `backend/app/schemas/reconciliation.py`.
- Move the SQLAlchemy model into `backend/app/db/models/reconciliation.py` and
  update Alembic metadata imports in `backend/migrations/env.py`.
- Move persistence into `backend/app/repositories/reconciliation.py`.
- Move application orchestration into `backend/app/services/reconciliation.py`.
- Add `backend/app/dependencies.py` as the composition root for settings,
  database sessions, repositories, and services needed by M1.5 routers.
- Add `backend/app/routers/__init__.py` as the router package boundary without
  adding endpoint modules yet.
- Update tests and imports to use the final paths.
- Remove the obsolete `backend/app/features/reconciliation/` package only after
  no imports reference it.

Required dependency signatures and test shape:

```python
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, load_settings
from app.db.session import get_session
from app.repositories.reconciliation import BaseReconciliationCaseRepository
from app.services.reconciliation import BaseReconciliationCaseService


def get_reconciliation_case_repository(
    session: Annotated[Session, Depends(get_session)],
) -> BaseReconciliationCaseRepository:
    """Build the request-scoped reconciliation repository.

    What: Wraps the current SQLAlchemy session in the repository used by the
        Base API service.
    Why: Routers should depend on repository composition instead of opening
        database sessions directly.

    Args:
        session: Request-scoped SQLAlchemy session from the database dependency.

    Returns:
        BaseReconciliationCaseRepository: Repository bound to the request
        session.
    """


def get_reconciliation_case_service(
    repository: Annotated[
        BaseReconciliationCaseRepository,
        Depends(get_reconciliation_case_repository),
    ],
    settings: Annotated[Settings, Depends(load_settings)],
) -> BaseReconciliationCaseService:
    """Build the request-scoped reconciliation application service.

    What: Composes the repository and configured confidence threshold into the
        Base API service.
    Why: M1.5 routers need one dependency that exposes use-case behavior
        without constructing services inline.

    Args:
        repository: Repository dependency for Base API case persistence.
        settings: Runtime settings containing the review confidence threshold.

    Returns:
        BaseReconciliationCaseService: Application service ready for router use.
    """
```

Dependency-composition test pseudocode:

```python
def test_reconciliation_service_dependency_composes_service(migrated_connection):
    session = Session(migrated_connection, expire_on_commit=False)
    repository = get_reconciliation_case_repository(session)
    settings = Settings(
        DATABASE_URL=LOCAL_DATABASE_URL,
        EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD=0.80,
    )

    service = get_reconciliation_case_service(repository, settings)

    assert isinstance(service, BaseReconciliationCaseService)
    created = service.create_case(valid_reconciliation_request())
    assert service.get_case(created.id) == created
```

### Refactor

- Keep the refactor behavior-preserving; do not add HTTP routes in this phase.
- Keep route handler modules deferred to M1.5 so M1.4 does not add placeholder endpoints.
- Do not add new dependencies, migrations, environment variables, runtime
  services, seed scripts, reset scripts, frontend files, Redis, Ollama, workers,
  auth, tenant context, or real LLM calls.
- Keep compatibility shims out unless a test proves they are needed during the
  same phase; final imports should use the new layer paths.

## What You Can Run After This Phase

```bash
cd backend
uv run python -m pytest tests/test_reconciliation_structure.py tests/features/reconciliation tests/test_health.py
uv run mypy app
uv run ruff check .
```

Expected outcome: the existing backend behavior passes through the new module
layout, and `/health` still works.

## Setup and Testing in Local Dev

Settings and configuration remain in `backend/.env` with `DATABASE_URL` and
`EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD=0.80`.

Local commands:

```bash
docker compose up -d postgres
cd backend
uv run alembic upgrade head
uv run python -m pytest tests/test_reconciliation_structure.py tests/features/reconciliation tests/test_health.py
uv run mypy app
uv run ruff check .
```

Multi-tenant coverage: N/A because Milestone 1 is intentionally non-tenantized.

Tenant-aware test cases: N/A because tenant routes are deferred.

Expected outcome: import-path, dependency-composition, persistence, validation,
decision, service, and health tests pass with no API endpoints added.

## Rollout Plan and Testing in QA and Staging

QA/staging steps:

1. Deploy the refactor with the same database migration head from M1.2.
2. Run backend tests and `/health` smoke checks.
3. Confirm no new HTTP routes are exposed by this phase.
4. Confirm Alembic can still load metadata from the new database model path.

Expected outcome: existing backend behavior remains available and the route
surface is unchanged.

Configuration changes: none.

Data setup or migration steps: none beyond the existing M1.2 migration.

## Rollout to Production

Production steps:

1. Confirm the deployment contains only module organization and dependency
   composition changes.
2. Run `/health` smoke check.
3. Confirm migration tooling can still import target metadata.
4. Roll back by redeploying the previous backend revision if import or startup
   checks fail.

Expected outcome: no user-visible API behavior changes.

Configuration changes: none.

Data setup or migration steps: none.

## SaaS Pre-Flight Disposition

| # | Item | Disposition | Evidence / Steps |
|---|------|-------------|------------------|
| 1 | Local dev multi-tenant coverage | N/A | Milestone 1 is non-tenantized and this phase does not add tenant paths. |
| 2 | Tenant-aware test cases | N/A | Tenant routes and tenant-scoped repositories are deferred. |
| 3 | Per-environment feature flag state | N/A | No feature flag is added; this is a behavior-preserving refactor. |
| 4 | Per-tenant production canary | N/A | No tenant model exists in Milestone 1. |
| 5 | Observability verification | N/A | Structured observability is deferred; startup and health checks verify the refactor. |
| 6 | Audit log verification | N/A | Audit logging is deferred. |
| 7 | Rate limit / quota verification | N/A | Rate limiting is deferred with auth/tenant work. |
| 8 | Webhook delivery verification | N/A | Webhooks are not in scope. |
| 9 | Rollback addresses in-flight tenant data | N/A | No tenant data or data migration changes; rollback is covered by previous backend revision redeploy. |
| 10 | Kill switch drill without redeploy | N/A | No feature flag exists; rollback is code redeploy before customer use. |

## Summary of Changes

- `backend/app/domain/reconciliation/contracts.py` (moved): Exports
  `ReconciliationStatus`, `ReconciliationCaseCreateV1`,
  `ReconciliationDecisionV1`, and `BaseReconciliationCase` from the domain
  layer named in [../DEFINITIONS.md](../DEFINITIONS.md#types).
- `backend/app/domain/reconciliation/decisions.py` (moved): Exports the pure
  validation and decision functions owned by
  [../DEFINITIONS.md](../DEFINITIONS.md#pure-functions).
- `backend/app/schemas/reconciliation.py` (moved): Exports the Pydantic API
  models matching [../API.md](../API.md#base-api-schemas).
- `backend/app/db/models/reconciliation.py` (moved): Exports the SQLAlchemy
  `Base` and reconciliation case model used by Alembic metadata.
- `backend/app/repositories/reconciliation.py` (moved): Exports
  `BaseReconciliationCaseRepository` for persistence.
- `backend/app/services/reconciliation.py` (moved): Exports
  `BaseReconciliationCaseService` and its repository protocol.
- `backend/app/dependencies.py` (new): Exports
  `get_reconciliation_case_repository` and `get_reconciliation_case_service`.
- `backend/app/routers/__init__.py` (new): Establishes the router package
  boundary without adding route handlers.
- `backend/migrations/env.py` (modify): Imports target metadata from the new DB
  model path.
- `backend/tests/test_reconciliation_structure.py` (new): Adds final-path import and
  dependency-composition tests.
- Existing backend tests (modify): Updates imports to the new layer paths.

## Code Generation Instructions

See `planning-conventions` -> Code Generation Instructions. Lint, types,
docstrings, commits, and change-summary rules apply unchanged.

<details>
<summary>Coverage Ledger</summary>

| ID | Category | Source | Pushed to (owner file) | Status |
|----|----------|--------|------------------------|--------|
| L1 | inherited | [../PLAN.md](../PLAN.md#milestone-1-base-api-development) M1.4 table row | -- | resolved |
| L2 | new-durable | Backend layer map from workforce-one study | [../ARCH.md](../ARCH.md#backend-layer-map) | resolved |
| L3 | new-durable | Layer responsibility definitions | [../DEFINITIONS.md](../DEFINITIONS.md#backend-layer-responsibilities) | resolved |
| L4 | new-durable | Structure-alignment test ownership | [../TESTING.md](../TESTING.md#milestone-1-base-api-tests) | resolved |
| L5 | new-durable | Reconciliation component location | [../SPEC.md](../SPEC.md#component-matching-and-reconciliation) | resolved |
| L6 | inherited | [../PLAN.md](../PLAN.md#milestone-1-base-api-development) M1.2 table row | -- | resolved |
| L7 | inherited | [../PLAN.md](../PLAN.md#milestone-1-base-api-development) M1.3 table row | -- | resolved |
| L8 | phase-local | Dependency composition functions for M1.5 router use | -- | phase-local |
| L9 | assumption | File moves are behavior-preserving and all imports can be updated in one phase | -- | to be verified by import-path and existing behavior tests |

</details>
