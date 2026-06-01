# PHASE-M2.3-CASE-LIST.md

## Executive Summary

This phase builds the first data screen: a stored reconciliation case list backed
by `GET /v1/reconciliation-cases`. It proves the frontend can consume the Base
API before any create form is introduced.

Expected outcome: users can open the local frontend, load stored case summaries,
see empty and error states, and retry failed loads.

Assumptions:

- M2.1 cleaned the scaffold and M2.2 added backend CORS plus API base config.
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

- Add frontend API DTO types that mirror the Base API list response from
  [../API.md](../API.md#base-api-schemas).
- Add a small `listReconciliationCases` client function that calls
  `GET /v1/reconciliation-cases` through the M2.2 API base URL helper.
- Replace the static shell center with a case list view in `App.tsx` or a small
  local component split if the file becomes hard to read.
- Render status, references, amounts, currency, review flag, and timestamps from
  each `ReconciliationCaseListItemV1`.
- Add retry behavior that re-runs the list request.
- Do not add frontend test tooling, frontend test files, or a frontend `test`
  script in this phase.

Pseudo code for loading:

```text
on app mount or retry:
    set state to loading
    call listReconciliationCases()
    if items is empty: set state to empty
    if items exists: set state to success(items)
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

Optional manual check with backend running:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

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
| Loading/empty/success/error states | inherited | [../TESTING.md](../TESTING.md#milestone-2-base-frontend-verification) | Required for first data screen. |
| No mock-only screens | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | Empty backend result must show empty UI, not fixtures. |
