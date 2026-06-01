# PHASE-M2.3-CASE-LIST.md

## Executive Summary

This phase builds the first data screen: a stored reconciliation case list backed
by `GET /v1/reconciliation-cases`. It proves the frontend can consume the Base
API before any create form is introduced.

Expected outcome: users can open the local frontend, load stored case summaries,
see empty and error states, and retry failed loads.

Assumptions:

- M2.1 cleaned the scaffold and M2.2 added backend CORS plus API base config.
- This phase starts on top of M2.2; confirm `frontend/src/config/api.ts`,
  `frontend/.env.example`, and backend CORS support exist before coding.
- The backend Base API is running locally and migrations have been applied.
- The list endpoint returns `ReconciliationCaseListResponseV1`.

P_bottom_up: about 220 production LOC for API types/client, list UI, and styles.
T_bottom_up: 0 frontend test LOC. Verification uses build, lint, and manual
browser checks against the local backend.

## Execution Plan

### Manual Acceptance Targets

- A successful `GET /v1/reconciliation-cases` response renders stored case
  summaries from the backend.
- An empty `items` response renders an empty state, not mock data.
- A failed request renders an error state with a retry action.
- Retrying re-runs the list request without reloading the whole page.

### Green

- Add `frontend/src/api/reconciliationCases.ts` exporting
  `ReconciliationStatus`, `ReconciliationCaseListItemV1`,
  `ReconciliationCaseListResponseV1`, and
  `listReconciliationCases(): Promise<ReconciliationCaseListResponseV1>`.
- `listReconciliationCases` calls `GET /v1/reconciliation-cases` through the
  M2.2 API base URL helper, checks `response.ok`, reads `error.message` from
  the API error envelope when available, and throws for non-2xx responses,
  malformed JSON, or a missing `items` array.
- Replace the static shell center in `frontend/src/App.tsx` with a case list
  view.
- Update `frontend/src/App.css` for list, state, retry, and responsive styles.
- Render status, references, amounts, currency, review flag, and timestamps from
  each `ReconciliationCaseListItemV1`. Use visible fallback text for nullable
  references, amounts, and currency, and never show minor-unit amounts as raw
  unlabeled cents.
- Add retry behavior that re-runs the list request.
- Do not add frontend test tooling, frontend test files, or a frontend `test`
  script in this phase.

Pseudo code for loading:

```text
on app mount or retry:
    set state to loading
    call listReconciliationCases()
    if items.length === 0: set state to empty
    else: set state to success(items)
    if request fails: set state to error(message)
```

### Refactor

- Keep list state local to the frontend app.
- Do not add routing, global state management, or table libraries.
- Keep create actions absent until M2.5.

## Setup and Testing in Local Dev

Environment variables:

```bash
# frontend/.env
VITE_RECONAI_API_BASE_URL=http://127.0.0.1:8000
```

Local commands:

```bash
cd frontend
npm run build
npm run lint
```

Manual check with backend running:

```bash
# Terminal 1, from repo root
docker compose up -d postgres
cd backend
uv run alembic upgrade head
uv run fastapi dev --host 127.0.0.1 --port 8000

# Terminal 2, from repo root after the backend is running
curl -X POST http://127.0.0.1:8000/v1/reconciliation-cases \
  -H 'Content-Type: application/json' \
  -d '{
    "external_reference": "CALL-M2-3",
    "customer_reference": "CUST-M2-3",
    "source_text": "Customer agreed to pay PKR 2,500 by June 10.",
    "extraction": {
      "schema_version": "agreement_extraction.v1",
      "agreed_amount_minor": 250000,
      "currency": "PKR",
      "payment_type": "FULL_PAYMENT",
      "due_date": "2026-06-10",
      "is_final_amount": true,
      "evidence_text": "Customer agreed to pay PKR 2,500 by June 10.",
      "confidence": 0.92,
      "needs_human_review": false
    },
    "actual_payment": {
      "paid_amount_minor": 250000,
      "currency": "PKR",
      "payment_date": "2026-06-09",
      "reference": "TXN-M2-3",
      "payment_method": "bank_transfer"
    }
  }'

# Terminal 3, from frontend/
npm run dev -- --host 127.0.0.1 --port 5173
```

Manual success check: open the Vite URL and confirm the `CALL-M2-3` row
appears. Manual empty check: run against an empty database. Manual error check:
stop the backend, reload, and confirm the retry state appears.

## What You Can Run After This Phase

With the backend running at `http://127.0.0.1:8000`, open the Vite frontend and
view stored reconciliation case summaries. If the database has no cases, the UI
shows an empty state rather than mock data.

## Rollout Notes

- Local: verify with a running backend and with an empty database.
- QA/Staging/Production: N/A until frontend deployment exists.
- Rollback: remove the list client/UI files; no backend or database state is
  affected.

## Summary of Changes

- Add frontend Base API list DTOs and client.
- Add the first real data UI for stored case summaries.
- Add manual verification coverage for list behavior.

## Out of Scope

- Detail loading, create form, seed scripts, mock-only screens, routing library,
  auth, tenants, dashboard, exports, frontend tests, and browser E2E tests.

## Coverage Ledger

| Item | Category | Source | Notes |
| --- | --- | --- | --- |
| View stored data before create | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | User reordered M2 so list precedes submit. |
| List response shape | inherited | [../API.md](../API.md#base-api-schemas) | Uses `ReconciliationCaseListResponseV1`. |
| Success, empty, error, and retry states | inherited | [../TESTING.md](../TESTING.md#milestone-2-base-frontend-verification) | Required for first data screen. |
| Loading state | phase-local | This phase manual acceptance targets | Required while the first request is pending. |
| No mock-only screens | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | Empty backend result must show empty UI, not fixtures. |
