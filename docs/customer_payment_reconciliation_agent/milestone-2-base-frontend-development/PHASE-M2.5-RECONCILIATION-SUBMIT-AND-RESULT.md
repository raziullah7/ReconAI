# PHASE-M2.5-RECONCILIATION-SUBMIT-AND-RESULT.md

## Executive Summary

This phase adds the first create flow after users can already view stored data.
The form builds `ReconciliationCaseCreateRequestV1`, submits it to
`POST /v1/reconciliation-cases`, displays the backend-owned decision response,
and updates the visible stored cases.

Expected outcome: users can manually submit LLM-shaped extraction data and
optional actual payment evidence, then see the deterministic backend decision.

Assumptions:

- M2.3 and M2.4 already provide list and detail viewing.
- The form does not call a real LLM; it collects the same shape that a future
  LLM adapter will emit.
- Amounts are entered in major units and converted to two-decimal minor units
  before sending the Base API request, matching the Milestone 2 note in
  [../UI_UX.md](../UI_UX.md#milestone-2-base-frontend-slice).

P_bottom_up: about 260 production LOC for form state, request building, create
client, result rendering, and styles.
T_bottom_up: 0 frontend test LOC. Verification uses build, lint, and manual
browser checks against the local backend.

## Execution Plan

### Manual Acceptance Targets

- Form values produce a `ReconciliationCaseCreateRequestV1` request with
  two-decimal major-unit amounts converted to minor-unit integers.
- Empty optional payment fields submit `actual_payment: null`.
- A successful `POST /v1/reconciliation-cases` response renders the backend
  decision and updates visible stored cases.
- Backend validation or network failures render an error and preserve entered
  form values.

### Green

- Add a pure request-building helper for `ReconciliationCaseCreateRequestV1`.
- Add `createReconciliationCase(input)` to the frontend API client.
- Add a form with fields for external reference, customer reference, source text,
  agreed amount, currency, payment type, due date, final amount flag, evidence
  text, confidence, human-review flag, optional actual paid amount, optional
  actual payment currency/date/reference/method.
- Convert major-unit amount inputs to two-decimal minor-unit integers before
  submitting. Reject values with more than two decimal places in local form
  validation.
- Submit to the Base API and render the returned decision status, amounts,
  difference, currency, reason, confidence, and review flag.
- Refresh the list or insert the created case into visible list state after a
  successful create.

Pseudo code for submit:

```text
on submit:
    validate required local form fields
    build ReconciliationCaseCreateRequestV1
    set submit state to loading
    call createReconciliationCase(request)
    if success:
        show decision result
        update visible list/detail state with response
    if failure:
        show error
        keep form values unchanged
```

### Refactor

- Keep request-building pure and separated from React state where it improves
  readability.
- Do not introduce form libraries until validation needs exceed this first form.

## Setup and Testing in Local Dev

Local commands:

```bash
cd frontend
npm run build
npm run lint
```

Manual check with backend running:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Expected manual behavior: submit a valid form, see the backend decision result,
and see the created case appear in the stored case UI.

## What You Can Run After This Phase

The local app can view stored cases, inspect details, create a new case from
manual LLM-shaped extraction input, and display the backend decision.

## Rollout Notes

- Local: verify valid submit, backend validation error, and network error.
- QA/Staging/Production: N/A until frontend deployment exists.
- Rollback: remove submit client/form changes; list and detail viewing remain.

## Summary of Changes

- Add create request builder and API client function.
- Add the create form and result view.
- Add manual verification coverage for request construction and submit behavior.

## Out of Scope

- Real LLM extraction, file upload, transcript submission, payment-ledger
  matching, review actions, auth, tenants, dashboard, exports, frontend tests,
  and browser E2E tests.

## Coverage Ledger

| Item | Category | Source | Notes |
| --- | --- | --- | --- |
| Submit comes after list/detail | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | User explicitly requested view before add. |
| Create request shape | inherited | [../API.md](../API.md#base-api-schemas) | Uses `ReconciliationCaseCreateRequestV1`. |
| Major-unit amount entry | inherited | [../UI_UX.md](../UI_UX.md#milestone-2-base-frontend-slice) | Convert to two-decimal minor units before API submit. |
| LLM remains mocked/manual | inherited | [../PLAN.md](../PLAN.md#development-shape) | No real LLM call in M2.5. |
