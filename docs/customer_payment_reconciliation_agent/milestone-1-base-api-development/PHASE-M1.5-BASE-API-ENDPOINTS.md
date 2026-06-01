# PHASE-M1.5-BASE-API-ENDPOINTS.md

## Executive Summary

This phase exposes the Base API behavior over HTTP. It adds a FastAPI router for
creating, listing, and fetching reconciliation cases, wires canonical error
envelopes for validation and not-found responses through explicit exception
handlers, and registers the router in the app factory.

Expected outcome: a local client can call `/v1/reconciliation-cases` and receive
stored backend-owned reconciliation decisions through the M1.4
router-service-repository dependency structure.

Assumptions:

- M1.2 repository, M1.3 validation/service behavior, and M1.4 layer
  structure exist.
- Milestone 1 remains unauthenticated and non-tenantized.
- List pagination uses `limit` and `offset` only in Milestone 1.

P_bottom_up: about 250 production LOC.
T_bottom_up: about 180 test LOC.

## Execution Plan

### Red

- `test_post_reconciliation_case_persists_and_returns_decision`
  - Summary: Posts a valid create request and expects a stored case response.
  - Mocks: FastAPI `TestClient`; database fixture from M1.2.
  - Assertions: Status is 201, response includes `id`, original snapshots,
    computed decision, and timestamps; the app uses
    `get_reconciliation_case_service` rather than constructing the service
    inside the route.

- `test_get_reconciliation_cases_returns_summaries`
  - Summary: Lists stored cases with `limit` and `offset`.
  - Mocks: FastAPI `TestClient`; seeded repository rows.
  - Assertions: Status is 200, newest-first items are returned, and detail-only
    snapshot fields are not required in summaries.

- `test_get_reconciliation_case_returns_detail_or_not_found`
  - Summary: Fetches one stored case and verifies unknown IDs use the error
    envelope.
  - Mocks: FastAPI `TestClient`; seeded repository row.
  - Assertions: Existing ID returns 200 detail; unknown ID returns 404 with
    `{ "error": { "code", "message", "request_id" } }`.

- `test_invalid_reconciliation_case_uses_error_envelope`
  - Summary: Posts invalid Pydantic payload data and valid-shape data rejected
    by service validation, then expects the canonical error shape.
  - Mocks: FastAPI `TestClient`.
  - Assertions: Pydantic validation returns 422, service validation returns 400,
    `error.code` is `ValidationFailed`, `error.message` is present,
    `error.request_id` is present, and the response body uses the
    [../API.md](../API.md#error-envelope) envelope.

### Green

- Add `backend/app/routers/errors.py` with error response helpers and FastAPI
  exception-handler registration for `RequestValidationError` and expected HTTP
  errors; route handlers map service `ValueError` validation failures to the
  same envelope with status 400.
- Add `backend/app/routers/reconciliation_cases.py` with the Base API router.
- Define the router prefix in the module with
  `APIRouter(prefix="/v1/reconciliation-cases", tags=["reconciliation"])`;
  [../../../backend/app/main.py](../../../backend/app/main.py) must call
  `include_router(reconciliation_cases.router)` without an additional prefix.
- Modify [../../../backend/app/main.py](../../../backend/app/main.py) to register
  the router and error handlers using the M1.4 dependency composition.

Required signatures and route shape:

```python
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.dependencies import get_reconciliation_case_service
from app.domain.reconciliation.contracts import ReconciliationStatus
from app.schemas.reconciliation import (
    ReconciliationCaseCreateRequestV1,
    ReconciliationCaseListResponseV1,
    ReconciliationCaseResponseV1,
)
from app.services.reconciliation import BaseReconciliationCaseService


def build_error_response(
    code: str,
    message: str,
    request_id: str,
) -> dict[str, dict[str, str]]:
    """Build the canonical API error envelope.

    What: Returns the shared error object used by Base API endpoints.
    Why: Clients need one predictable failure shape before frontend work starts.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable explanation.
        request_id: Request correlation value, or a local placeholder before
            request context exists.

    Returns:
        dict[str, dict[str, str]]: Canonical error envelope.
    """


def register_error_handlers(application: FastAPI) -> None:
    """Register canonical Base API error handlers.

    What: Installs handlers that convert FastAPI validation errors and expected
        route errors into the shared error envelope.
    Why: The API contract requires non-2xx responses to use one predictable
        shape.

    Args:
        application: FastAPI app created by `create_app`.

    States / Side Effects:
        Mutates the FastAPI application exception-handler registry.
    """


router = APIRouter(prefix="/v1/reconciliation-cases", tags=["reconciliation"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_reconciliation_case(
    input: ReconciliationCaseCreateRequestV1,
    service: Annotated[
        BaseReconciliationCaseService,
        Depends(get_reconciliation_case_service),
    ],
) -> ReconciliationCaseResponseV1:
    ...


@router.get("")
def list_reconciliation_cases(
    service: Annotated[
        BaseReconciliationCaseService,
        Depends(get_reconciliation_case_service),
    ],
    status_filter: Annotated[ReconciliationStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ReconciliationCaseListResponseV1:
    ...


@router.get("/{case_id}")
def get_reconciliation_case(
    case_id: UUID,
    service: Annotated[
        BaseReconciliationCaseService,
        Depends(get_reconciliation_case_service),
    ],
) -> ReconciliationCaseResponseV1:
    ...
```

Router pseudo code:

```text
POST /v1/reconciliation-cases:
    receive ReconciliationCaseCreateRequestV1
    call injected BaseReconciliationCaseService.create_case
    if service raises ValueError: return 400 ValidationFailed envelope
    return 201 ReconciliationCaseResponseV1

GET /v1/reconciliation-cases:
    parse optional status, limit, offset
    call injected BaseReconciliationCaseService.list_cases
    return ReconciliationCaseListResponseV1(items=items)

GET /v1/reconciliation-cases/{case_id}:
    call injected BaseReconciliationCaseService.get_case
    if missing: return NotFound envelope with request_id
    return detail

RequestValidationError handler:
    return 422 ValidationFailed envelope with request_id

Expected HTTP error handler:
    return the supplied status code with NotFound or ValidationFailed envelope
```

### Refactor

- Keep HTTP functions thin and use the M1.4 service dependency for decision work.
- Keep Milestone 1 route paths non-tenantized.
- Do not add auth, idempotency records, cursor pagination, frontend, workers,
  Redis, Ollama, or real LLM calls.

### Post-M1 Correction

M1.5 planned the list endpoint response as
`dict[str, list[ReconciliationCaseListItemV1]]` and returned
`{"items": items}` directly. That JSON shape was correct, but the phase missed a
named collection-envelope DTO. After Milestone 1 was merged, this was corrected
by introducing `ReconciliationCaseListResponseV1` while keeping the public JSON
shape unchanged.

## Setup and Testing in Local Dev

Settings and configuration live in `backend/.env`: `DATABASE_URL` and
`EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD=0.80`.

Start from the backend folder and create the local `.env` file:

```bash
cd backend
cp .env.example .env
```

Local commands:

```bash
docker compose up -d postgres
cd backend
uv run alembic upgrade head
uv run python -m pytest tests/test_reconciliation_structure.py tests/features/reconciliation/test_api.py tests/test_health.py
uv run fastapi dev --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/v1/reconciliation-cases
uv run mypy app
uv run ruff check .
```

Multi-tenant coverage: N/A because Base API is explicitly non-tenantized.

Tenant-aware test cases: N/A because tenant paths are deferred.

Expected outcome: structure, create/list/detail API, validation-envelope, and
`/health` tests pass.

## Rollout Plan and Testing in QA and Staging

QA/staging steps:

1. Run migrations from M1.2.
2. Deploy the backend with the Base API router enabled by code.
3. Run create/list/detail API tests against the environment.
4. Confirm invalid and not-found responses use the canonical envelope.

Expected outcome: QA/staging can exercise the Base API without frontend or LLM.

Configuration changes: threshold setting only.

Data setup or migration steps: M1.2 migration must already be applied.

## Rollout to Production

Production steps:

1. Confirm M1.2 migration is applied.
2. Deploy backend with the Base API router.
3. Run `/health` smoke check.
4. Run one create/list/detail smoke check using a non-production sample payload
   if production testing policy allows it; otherwise run in staging only and
   verify route registration through OpenAPI.

Expected outcome: Base API endpoints are available for later frontend work.

Configuration changes: threshold setting only.

Data setup or migration steps: none beyond M1.2.

## SaaS Pre-Flight Disposition

| # | Item | Disposition | Evidence / Steps |
|---|------|-------------|------------------|
| 1 | Local dev multi-tenant coverage | N/A | Base API is non-tenantized. |
| 2 | Tenant-aware test cases | N/A | Tenant routes are deferred. |
| 3 | Per-environment feature flag state | N/A | No feature flag exists for M1.5; threshold config stays in `backend/.env`. |
| 4 | Per-tenant production canary | N/A | No tenant model exists. |
| 5 | Observability verification | N/A | Structured observability is deferred; smoke checks verify responses. |
| 6 | Audit log verification | N/A | Audit logging is deferred. |
| 7 | Rate limit / quota verification | N/A | Rate limiting is deferred with auth/tenant work. |
| 8 | Webhook delivery verification | N/A | Webhooks are not in scope. |
| 9 | Rollback addresses in-flight tenant data | Addressed | Rollback removes route registration; stored cases remain in DB for later migration policy. |
| 10 | Kill switch drill without redeploy | N/A | No feature flag exists; rollback is code redeploy before customer use. |

## Summary of Changes

- `backend/app/routers/errors.py` (new): Adds canonical error envelope helper
  and exception-handler registration for L5 and L8.
- `backend/app/routers/reconciliation_cases.py` (new): Adds create/list/detail
  routes for L1 and L4 while calling the L2 service methods through dependency
  injection.
- [../../../backend/app/main.py](../../../backend/app/main.py) (modify): Registers
  the Base API router and error handlers for L3.
- `backend/tests/features/reconciliation/test_api.py` (new): Adds endpoint tests for L4.

## Code Generation Instructions

See `planning-conventions` -> Code Generation Instructions. Lint, types,
docstrings, commits, and change-summary rules apply unchanged.

<details>
<summary>Coverage Ledger</summary>

| ID | Category | Source | Pushed to (owner file) | Status |
|----|----------|--------|------------------------|--------|
| L1 | inherited | [../API.md](../API.md#base-api-endpoints) | -- | resolved |
| L2 | inherited | [../DEFINITIONS.md](../DEFINITIONS.md#application-service) | -- | resolved |
| L3 | inherited | [../PLAN.md](../PLAN.md#milestone-1-base-api-development) M1.5 table row | -- | resolved |
| L4 | inherited | [../TESTING.md](../TESTING.md#milestone-1-base-api-tests) | -- | resolved |
| L5 | phase-local | Error envelope helper needed by endpoint errors | -- | phase-local |
| L6 | inherited | [../PLAN.md](../PLAN.md#milestone-1-base-api-development) M1.2, M1.3, and M1.4 order | -- | resolved |
| L7 | assumption | Current M1.4 code exposes `get_reconciliation_case_service` from `app.dependencies` for router injection. | [../../../backend/app/dependencies.py](../../../backend/app/dependencies.py) | verified by read-only spot-check |
| L8 | inherited | [../API.md](../API.md#error-envelope) | -- | resolved |

</details>
