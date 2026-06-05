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
- M2.5 uses schema-safe local validation only: block invalid formats, but allow
  blank nullable Base API fields so the backend can produce review statuses.
- M2.5 hides optional LLM metadata fields. Do not render `model_name` or
  `raw_llm_output`, and omit them from the create request.
- M2.5 keeps the frontend light-only. Do not add dark-mode classes or
  custom theme switching until a later dedicated design/theme phase.

P_bottom_up: about 300 production LOC for form state, request building, create
client, submit route, result rendering, route invalidation, and styles.
T_bottom_up: 0 frontend test LOC. Verification uses build, lint, and manual
browser checks against the local backend.

## Execution Plan

### Manual Acceptance Targets

- Form values produce a `ReconciliationCaseCreateRequestV1` request with
  two-decimal major-unit amounts converted to minor-unit integers.
- Blank amount fields submit `null`; amount values with more than two decimal
  places are rejected before the request is sent.
- Empty optional payment fields submit `actual_payment: null`; partially filled
  payment fields submit an `actual_payment` object with blank optional fields as
  `null`.
- A successful `POST /v1/reconciliation-cases` response renders the backend
  decision and offers navigation to the created detail route.
- Backend validation or network failures render an error and preserve entered
  form values.
- `/reconciliation-cases/new` can be opened directly in the browser.
- The existing list/detail experience includes a visible action that navigates
  to `/reconciliation-cases/new`.

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
  to `frontend/src/api/reconciliation-cases.ts`. It sends JSON to
  `POST /v1/reconciliation-cases`, parses the existing
  `ReconciliationCaseResponseV1`, and uses the same canonical error-envelope
  handling as the list/detail client functions.
- Add `frontend/src/routes/reconciliation-cases/new.tsx` as the submit route.
  Keep the route file focused on the TanStack `Route` export and route options,
  matching the M2.4 route-module pattern.
- Add route-local submit pieces under
  `frontend/src/routes/reconciliation-cases/-components`, with
  `case-submit-route.tsx` owning submit/result state and smaller form/result
  components extracted only as needed for readability.
- Add a form with fields for external reference, customer reference, source text,
  agreed amount, currency, payment type, due date, final amount flag, evidence
  text, confidence, human-review flag, optional actual paid amount, optional
  actual payment currency/date/reference/method. Do not render user-editable
  schema version, `model_name`, or `raw_llm_output` fields; the builder owns the
  schema version constant and omits the hidden metadata fields.
- Convert major-unit amount inputs to two-decimal minor-unit integers before
  submitting. Reject values with more than two decimal places in local form
  validation, but do not require amount or currency fields that the Base API
  contract allows to be `null`.
- Submit to the Base API and render the returned decision status, amounts,
  difference, currency, reason, confidence, and review flag.
- After successful create, call `router.invalidate()` after the response is
  stored in local submit state so the list loader refreshes on the next list
  visit. Use `response.id` to render a TanStack Router `Link` to the created
  detail route and a second action back to `/reconciliation-cases`.
- Add a visible TanStack Router `Link` to `/reconciliation-cases/new` from the
  case list and keep the detail screen able to navigate back to list before
  creating another case from the list.
- Regenerate and commit `frontend/src/routeTree.gen.ts` after adding the submit
  route.

Pseudo code for submit:

```text
on submit:
    validate local form formats without requiring nullable API fields
    build ReconciliationCaseCreateRequestV1 with schema_version constant
    convert blank optional fields to null
    set actual_payment to null only when all payment fields are blank
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
- Keep submit-specific components route-local and preserve the M2.4 split
  between route files and render/state components.

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

Expected manual behavior: open the create route directly or from the list,
submit a valid form, see the backend decision result, open the created detail
route, then return to the refreshed stored case list.

## What You Can Run After This Phase

The local app can view stored cases, inspect details, create a new case from
manual LLM-shaped extraction input, display the backend decision, and navigate
between list, detail, and submit routes.

## Rollout Notes

- Local: verify direct `/reconciliation-cases/new` access, list-to-create
  navigation, valid submit, local amount-format validation, backend validation
  error, network error, created detail navigation through `response.id`, and
  refreshed list after returning.
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
- Add route-local submit components under
  `frontend/src/routes/reconciliation-cases/-components`.
- Modify the case list UI so users can navigate to `/reconciliation-cases/new`.
- Regenerate and commit `frontend/src/routeTree.gen.ts`.
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
| Schema-safe validation | user decision | M2.5 planning sync | Local validation blocks invalid formats but allows nullable API fields. |
| Hidden LLM metadata | user decision | M2.5 planning sync | Do not expose `model_name` or `raw_llm_output` in this first form. |
