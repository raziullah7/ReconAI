# TESTING.md

> Status: Testing should grow with the system. Early scaffold phases should
> have a few useful backend tests, not a large suite of placeholder or meta
> tests.

## Current Testing Policy

- Test behavior that exists now.
- Avoid broad folder-shape tests unless the structure is the actual feature.
- Do not add browser, backend integration, seed, or reset scripts unless the
  phase explicitly needs them.
- Keep scaffold phases to roughly 1-3 focused tests per subsystem.
- Add frontend tests only when the frontend setup phase exists.
- Add more tests when persistence, tenant isolation, auth, workers, or
  reconciliation rules actually exist.

## Phase 1 Tests

Backend:

- Settings require only `DATABASE_URL`.
- Compose declares only the Postgres service.
- Health endpoint returns the stable app-shell response.

Frontend:

- No frontend tests yet. The frontend is intentionally deferred.

## Milestone 1 Base API Tests

Milestone 1 should add focused tests only for the behavior it introduces.

Validation tests:

- Accept a valid `AgreementExtractionInputV1` fixture.
- Reject invalid amount, invalid confidence, invalid currency, missing evidence
  for low-confidence data, and unsupported `payment_type`.
- Accept an `ActualPaymentInputV1` fixture with minor-unit money and matching
  currency.
- Route supplied actual payment evidence with missing amount or currency to
  `NEEDS_REVIEW` during decision-making.

Decision tests:

- Exact amount and currency match returns `RECONCILED`.
- Paid amount below agreed amount returns `UNDERPAID` unless the payment type is
  explicitly partial-like, then returns `PARTIAL_PAYMENT`.
- Paid amount above agreed amount returns `OVERPAID`.
- Missing actual payment returns `PAYMENT_NOT_FOUND`.
- Confidence below `0.80`, extraction review flag, missing agreed amount,
  incomplete actual payment evidence, or currency mismatch returns
  `NEEDS_REVIEW`.
- Difference is always `paid_amount_minor - agreed_amount_minor` when both
  values exist.

Persistence tests:

- Repository creates a case with extraction and payment snapshots.
- Repository lists cases in newest-first order.
- Repository fetches one case by ID and returns not-found for an unknown ID.

Service tests:

- Service create validates input, computes a decision, persists snapshots, and
  returns a response model.
- Service list and get map repository projections to API response models without
  adding HTTP behavior.

API tests:

- `POST /v1/reconciliation-cases` persists and returns the computed decision.
- `GET /v1/reconciliation-cases` returns stored case summaries.
- `GET /v1/reconciliation-cases/{case_id}` returns the stored detail.
- Invalid payloads use the canonical error envelope from [API.md](API.md).

Not in Milestone 1 tests:

- Real LLM calls.
- Frontend tests.
- Tenant isolation.
- Auth or role checks.
- Redis, worker, queue, or Ollama behavior.
- CSV imports or payment-ledger matching.

## Later Test Growth

| Milestone Area | Test Growth |
| --- | --- |
| Base frontend | component and API-client tests after frontend setup exists |
| LLM integration | parser fixtures, adapter contract tests, and invalid-output cases |
| Tenant context | tenant isolation unit tests |
| Auth | protected route and permission tests |
| Customers/payments | API behavior and repository tests |
| Call intake | upload/transcript and storage boundary tests |
| Redis/queue | queue enqueue/dequeue smoke tests |
| Workers | status transition and retry tests |
| Reconciliation against ledger | table-driven matching and rule tests |
| Review workflow | review action and audit tests |
| Dashboard/export | UI smoke and export contract tests |

## Tooling

- Backend: pytest from `backend/` with `uv run python -m pytest`.
- Backend types: `uv run mypy app`.
- Backend lint: `uv run ruff check .`.
- Frontend: deferred until the frontend setup phase.
- Browser E2E: deferred until the UI has real workflows.
- Load/performance tests: deferred until APIs stabilize.
