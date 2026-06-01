# PHASE-M2.4-CASE-DETAIL.md

## Executive Summary

This phase adds stored case detail viewing backed by
`GET /v1/reconciliation-cases/{case_id}`. It builds on the case list so users can
inspect extraction, payment evidence, and backend decision data before the
frontend can create cases.

Expected outcome: selecting a stored case loads and displays its detail without
losing the list context.

Assumptions:

- M2.3 list UI exists and renders stored case IDs.
- The backend detail endpoint returns `ReconciliationCaseResponseV1` and uses
  the canonical error envelope for not-found responses.
- No router library is needed; selection can stay in local React state.

P_bottom_up: about 190 production LOC for detail client, detail UI, and styles.
T_bottom_up: about 120 test LOC for client and component behavior tests.

## Execution Plan

### Red

- `api_client_gets_reconciliation_case_detail`
  - Summary: Proves the frontend client fetches a detail URL by case ID.
  - Mocks: Stubbed `fetch`.
  - Assertions: The client calls `/v1/reconciliation-cases/{case_id}` and
    returns a typed `ReconciliationCaseResponseV1`.

- `case_detail_renders_success_and_error_states`
  - Summary: Proves selection loads detail while preserving the list.
  - Mocks: Stubbed list and detail clients.
  - Assertions: Selecting a case shows loading, renders extraction/payment/
    decision fields on success, and renders an error state for failed detail
    requests.

### Green

- Add detail DTO types that mirror `ReconciliationCaseResponseV1` from
  [../API.md](../API.md#base-api-schemas), reusing shared DTOs from M2.3.
- Add `getReconciliationCase(caseId: string)` to the frontend API client.
- Update the case list UI so each row/card can select one case.
- Add a detail panel that displays external reference, customer reference,
  extraction evidence, agreed amount, actual payment, backend decision status,
  reason, review flag, confidence, and timestamps.
- Add not-found/network error handling for the detail panel without clearing the
  already loaded list.

Pseudo code for selection:

```text
when user selects a case:
    store selected case id
    set detail state to loading
    call getReconciliationCase(id)
    if success: set detail state to success(detail)
    if not found or network error: set detail state to error(message)
```

### Refactor

- Extract small formatting helpers only if repeated amount/date formatting makes
  the UI harder to read.
- Do not add URL routing until navigation requirements are real.

## Setup and Testing in Local Dev

Local commands:

```bash
cd frontend
npm run test -- --run
npm run build
npm run lint
```

Manual check:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Expected manual behavior: load the list, select a stored case, and inspect its
detail panel.

## What You Can Run After This Phase

With the backend running, the frontend can list stored cases and inspect a case
detail. It still cannot submit a new case.

## Rollout Notes

- Local: verify detail success and a failed/not-found detail state.
- QA/Staging/Production: N/A until frontend deployment exists.
- Rollback: remove detail client/UI changes; list behavior from M2.3 remains the
  fallback.

## Summary of Changes

- Add detail client behavior.
- Add selectable list/detail interaction.
- Add focused tests for detail loading and error handling.

## Out of Scope

- Create form, editing, review actions, URL routing, auth, tenant filtering,
  audit history, payment candidate matching, and browser E2E tests.

## Coverage Ledger

| Item | Category | Source | Notes |
| --- | --- | --- | --- |
| Detail endpoint shape | inherited | [../API.md](../API.md#base-api-endpoints) | Uses M1 `GET /v1/reconciliation-cases/{case_id}`. |
| Detail after list | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | Preserves view-before-create order. |
| Detail error handling | inherited | [../TESTING.md](../TESTING.md#milestone-2-base-frontend-tests) | Missing/failed detail must not clear list. |
| Local React state selection | phase-local | This phase assumptions | Avoids router dependency in M2.4. |
