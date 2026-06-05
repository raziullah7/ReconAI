# PHASE-M2.5-RECONCILIATION-SUBMIT-AND-RESULT.md

## Executive Summary

This phase adds the first create flow after users can already view stored data.
The form builds `ReconciliationCaseCreateRequestV1`, submits it to
`POST /v1/reconciliation-cases`, displays the backend-owned decision response,
and offers route navigation to the created case detail.

Expected outcome: users can manually submit LLM-shaped extraction data and
optional actual payment evidence, then see the deterministic backend decision.

Assumptions:

- M2.3 and M2.4 already provide list and detail viewing.
- M2.3 introduced TanStack Router, and M2.4 added the detail route.
- The form does not call a real LLM; it collects the same shape that a future
  LLM adapter will emit.
- Amounts are entered in major units and converted to two-decimal minor units
  before sending the Base API request, matching the Milestone 2 note in
  [../UI_UX.md](../UI_UX.md#milestone-2-base-frontend-slice).

P_bottom_up: about 300 production LOC for form state, request building, create
client, submit route, result rendering, route invalidation, and styles.
T_bottom_up: 0 frontend test LOC. Verification uses build, lint, and manual
browser checks against the local backend.

## Execution Plan

### Manual Acceptance Targets

- Form values produce a `ReconciliationCaseCreateRequestV1` request with
  two-decimal major-unit amounts converted to minor-unit integers.
- Empty optional payment fields submit `actual_payment: null`.
- A successful `POST /v1/reconciliation-cases` response renders the backend
  decision and offers navigation to the created detail route.
- Backend validation or network failures render an error and preserve entered
  form values.
- `/reconciliation-cases/new` can be opened directly in the browser.

### Red

- N/A: Milestone 2 frontend phases intentionally do not add frontend tests or
  frontend test tooling. Verification uses build, lint, and manual browser
  checks from [../TESTING.md](../TESTING.md#milestone-2-base-frontend-verification).

### Green

- Add `frontend/src/routes/reconciliation-cases/-utils/create-request.ts` with
  `buildReconciliationCaseCreateRequest(form: ReconciliationCaseCreateFormState): ReconciliationCaseCreateRequestV1`.
  The builder injects `extraction.schema_version` as the constant
  `agreement_extraction.v1`.
- Add `createReconciliationCase(input: ReconciliationCaseCreateRequestV1): Promise<ReconciliationCaseResponseV1>`
  to `frontend/src/api/reconciliation-cases.ts`. It uses the same canonical
  error-envelope handling as the list/detail client functions.
- Add `frontend/src/routes/reconciliation-cases/new.tsx` as the submit route.
- Add a form with fields for external reference, customer reference, source text,
  agreed amount, currency, payment type, due date, final amount flag, evidence
  text, confidence, human-review flag, optional actual paid amount, optional
  actual payment currency/date/reference/method. Do not render a user-editable
  schema version field; the builder owns that constant.
- Convert major-unit amount inputs to two-decimal minor-unit integers before
  submitting. Reject values with more than two decimal places in local form
  validation.
- Submit to the Base API and render the returned decision status, amounts,
  difference, currency, reason, confidence, and review flag.
- After successful create, call `router.invalidate()` after the response is
  stored in local submit state so the list loader refreshes on the next list
  visit. Use `response.id` to render a TanStack Router `Link` to the created
  detail route and a second action back to `/reconciliation-cases`.

Pseudo code for submit:

```text
on submit:
    validate required local form fields
    build ReconciliationCaseCreateRequestV1 with schema_version constant
    set submit state to loading
    call createReconciliationCase(request)
    if success response:
        store response in submit result state
        call router.invalidate()
        show View created case link using response.id
        show Back to list action
    if failure:
        show error
        keep form values unchanged
```

### Refactor

- Keep request-building pure and separated from React state where it improves
  readability.
- Do not introduce form libraries until validation needs exceed this first form.
- Use HeroUI primitives and Tailwind utilities; do not add `frontend/src/features`,
  `frontend/src/ui-kit`, React Query, or router devtools.

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
open the created detail route, then return to the refreshed stored case list.

## What You Can Run After This Phase

The local app can view stored cases, inspect details, create a new case from
manual LLM-shaped extraction input, display the backend decision, and navigate
between list, detail, and submit routes.

## Rollout Notes

- Local: verify valid submit, backend validation error, network error, created
  detail navigation through `response.id`, and refreshed list after returning.
- QA/Staging/Production: N/A until frontend deployment exists.
- Rollback: remove submit client/form/route changes; list and detail viewing
  remain.

### SaaS Pre-Flight Dispositions

| Concern | Disposition |
| --- | --- |
| Local dev multi-tenant coverage | N/A: M2 uses the non-tenantized Base API. |
| Tenant-aware test cases | N/A: frontend tests are deferred for Milestone 2. |
| Per-environment feature flags | N/A: no frontend deployment or flags in M2.5. |
| Per-tenant production canary | N/A: no production rollout in this phase. |
| Observability verification | N/A: local Vite-only screen with no telemetry. |
| Audit log verification | N/A: Base API create audit UI is not in M2.5. |
| Rate limit / quota verification | N/A: Base API rate limits are deferred. |
| Webhook delivery verification | N/A: no webhooks are emitted. |
| Rollback includes tenant data | N/A: frontend-only change; created local cases remain backend state. |
| Kill switch drill | N/A: no deployed flag or kill switch exists yet. |

## Code Generation Instructions

Follow [planning-conventions Code Generation Instructions](../../../.agents/skills/planning-conventions/SKILL.md#code-generation-instructions).
For this phase: keep TypeScript explicit at exported boundaries, avoid
frontend tests/test scripts, avoid router devtools, and keep submit components
route-local while using HeroUI primitives.

## Summary of Changes

- Modify `frontend/src/api/reconciliation-cases.ts` with
  `createReconciliationCase(input: ReconciliationCaseCreateRequestV1): Promise<ReconciliationCaseResponseV1>`.
- Add `frontend/src/routes/reconciliation-cases/new.tsx` for
  `/reconciliation-cases/new`.
- Add `frontend/src/routes/reconciliation-cases/-utils/create-request.ts` with
  `buildReconciliationCaseCreateRequest(form: ReconciliationCaseCreateFormState): ReconciliationCaseCreateRequestV1`.
- Add create request builder and API client function.
- Add the route-based create form and result view.
- Add manual verification coverage for request construction and submit behavior.

## Out of Scope

- Real LLM extraction, file upload, transcript submission, payment-ledger
  matching, review actions, auth, tenants, dashboard, exports, frontend tests,
  and browser E2E tests.

## Coverage Ledger

| Item | Category | Source | Notes |
| --- | --- | --- | --- |
| Submit comes after list/detail | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | User explicitly requested view before add. |
| Submit route follows TanStack Router structure | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | M2.3 introduces file routes. |
| Create request shape | inherited | [../API.md](../API.md#base-api-schemas) | Uses `ReconciliationCaseCreateRequestV1`. |
| Major-unit amount entry | inherited | [../UI_UX.md](../UI_UX.md#milestone-2-base-frontend-slice) | Convert to two-decimal minor units before API submit. |
| LLM remains mocked/manual | inherited | [../PLAN.md](../PLAN.md#development-shape) | No real LLM call in M2.5. |
| Schema version injection | inherited | [../API.md](../API.md#base-api-schemas) | Builder must set `agreement_extraction.v1`. |
| M2.3/M2.4 routes exist | assumption | This phase assumptions | Requires list/detail routes and generated route tree before submit route. |
