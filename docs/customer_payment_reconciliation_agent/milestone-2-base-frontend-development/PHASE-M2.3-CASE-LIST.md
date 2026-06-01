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
T_bottom_up: about 140 test LOC for API-client and component behavior tests.

## Execution Plan

### Red

- `api_client_lists_reconciliation_cases`
  - Summary: Proves the frontend client fetches
    `/v1/reconciliation-cases` and validates the `items` envelope.
  - Mocks: Stubbed `fetch`.
  - Assertions: The client calls the configured API base URL and returns typed
    list items.

- `case_list_renders_success_empty_and_error_states`
  - Summary: Proves the UI handles the first Base API screen states.
  - Mocks: Stubbed list client.
  - Assertions: Loading text appears while pending, empty text appears for no
    items, summaries appear for success, and an error state includes retry.

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
- Add focused frontend test tooling only if it does not already exist: `vitest`,
  `@testing-library/react`, `@testing-library/jest-dom`, and `jsdom`. Use
  stubbed `fetch`; do not add browser E2E tooling.
- Add a `test` script in `frontend/package.json` that runs `vitest`.

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
npm run test -- --run
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
- Add focused frontend tests for list behavior.

## Out of Scope

- Detail loading, create form, seed scripts, mock-only screens, routing library,
  auth, tenants, dashboard, exports, and browser E2E tests.

## Coverage Ledger

| Item | Category | Source | Notes |
| --- | --- | --- | --- |
| View stored data before create | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | User reordered M2 so list precedes submit. |
| List response shape | inherited | [../API.md](../API.md#base-api-schemas) | Uses `ReconciliationCaseListResponseV1`. |
| Loading/empty/success/error states | inherited | [../TESTING.md](../TESTING.md#milestone-2-base-frontend-tests) | Required for first data screen. |
| No mock-only screens | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | Empty backend result must show empty UI, not fixtures. |
