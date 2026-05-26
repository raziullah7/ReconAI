# PHASE-M1.4-BASE-API-ENDPOINTS.md

## Executive Summary

This phase exposes the Base API behavior over HTTP. It adds a FastAPI router for
creating, listing, and fetching reconciliation cases, wires canonical error
envelopes for validation and not-found responses, and registers the router in
the app factory.

Expected outcome: a local client can call `/v1/reconciliation-cases` and receive
stored backend-owned reconciliation decisions.

Assumptions:

- M1.2 repository and M1.3 validation/service layers exist.
- Milestone 1 remains unauthenticated and non-tenantized.
- List pagination uses `limit` and `offset` only in Milestone 1.

P_bottom_up: about 310 production LOC.
T_bottom_up: about 220 test LOC.

## Execution Plan

### Red

- `test_post_reconciliation_case_persists_and_returns_decision`
  - Summary: Posts a valid create request and expects a stored case response.
  - Mocks: FastAPI `TestClient`; database fixture from M1.2.
  - Assertions: Status is 201, response includes `id`, original snapshots,
    computed decision, and timestamps.

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
  - Summary: Posts invalid payload data and expects the canonical error shape.
  - Mocks: FastAPI `TestClient`.
  - Assertions: Status is 422 or 400 according to FastAPI validation boundary,
    and the response body uses the [../API.md](../API.md#error-envelope)
    envelope.

### Green

- Add `backend/app/api/errors.py` with an error response helper.
- Add `backend/app/api/reconciliation_cases.py` with the Base API router.
- Modify [../../../backend/app/main.py](../../../backend/app/main.py) to include the
  router under `/v1/reconciliation-cases`.

Required signatures:

```python
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
```

Router pseudo code:

```text
POST /v1/reconciliation-cases:
    parse ReconciliationCaseCreateRequestV1
    call BaseReconciliationCaseService.create_case
    return 201 ReconciliationCaseResponseV1

GET /v1/reconciliation-cases:
    parse optional status, limit, offset
    call BaseReconciliationCaseService.list_cases
    return {"items": items}

GET /v1/reconciliation-cases/{case_id}:
    call BaseReconciliationCaseService.get_case
    if missing: raise not-found with error envelope
    return detail
```

### Refactor

- Keep HTTP functions thin and move decision work into M1.3 service code.
- Keep Milestone 1 route paths non-tenantized.
- Do not add auth, idempotency records, cursor pagination, frontend, workers,
  Redis, Ollama, or real LLM calls.

## Setup and Testing in Local Dev

Settings and configuration: `DATABASE_URL` and
`EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD=0.80`.

Environment variables:

```bash
DATABASE_URL=postgresql://reconai:reconai@localhost:5432/reconai
EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD=0.80
```

Local commands:

```bash
docker compose up -d postgres
cd backend
uv run alembic upgrade head
uv run python -m pytest tests/features/reconciliation/test_api.py
DATABASE_URL=postgresql://reconai:reconai@localhost:5432/reconai uv run fastapi dev --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/v1/reconciliation-cases
uv run mypy app
uv run ruff check .
```

Multi-tenant coverage: N/A because Base API is explicitly non-tenantized.

Tenant-aware test cases: N/A because tenant paths are deferred.

Expected outcome: create/list/detail API tests pass and `/health` still works.

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
| 3 | Per-environment feature flag state | Addressed | No feature flag; threshold is `0.80` in all environments. |
| 4 | Per-tenant production canary | N/A | No tenant model exists. |
| 5 | Observability verification | N/A | Structured observability is deferred; smoke checks verify responses. |
| 6 | Audit log verification | N/A | Audit logging is deferred. |
| 7 | Rate limit / quota verification | N/A | Rate limiting is deferred with auth/tenant work. |
| 8 | Webhook delivery verification | N/A | Webhooks are not in scope. |
| 9 | Rollback addresses in-flight tenant data | Addressed | Rollback removes route registration; stored cases remain in DB for later migration policy. |
| 10 | Kill switch drill without redeploy | N/A | No feature flag exists; rollback is code redeploy before customer use. |

## Summary of Changes

- `backend/app/api/errors.py` (new): Adds canonical error envelope helper for L1.
- `backend/app/api/reconciliation_cases.py` (new): Adds create/list/detail routes for L2.
- [../../../backend/app/main.py](../../../backend/app/main.py) (modify): Registers the Base API router for L3.
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
| L3 | inherited | [../PLAN.md](../PLAN.md#m14-base-api-endpoints) | -- | resolved |
| L4 | inherited | [../TESTING.md](../TESTING.md#milestone-1-base-api-tests) | -- | resolved |
| L5 | phase-local | Error envelope helper needed by endpoint errors | -- | phase-local |
| L6 | assumption | M1.2 and M1.3 are implemented first | -- | open |

</details>
