# PHASE-M2.4-CASE-DETAIL.md

## Executive Summary

This phase adds stored case detail viewing backed by
`GET /v1/reconciliation-cases/{case_id}`. It builds on the case list so users can
inspect extraction, payment evidence, and backend decision data before the
frontend can create cases.

Expected outcome: selecting a stored case loads and displays its detail without
losing browser navigation context.

Assumptions:

- M2.3 list UI exists and renders stored case IDs.
- M2.3 introduced TanStack Router, the root route shell, and
  `/reconciliation-cases`.
- The backend detail endpoint returns `ReconciliationCaseResponseV1` and uses
  the canonical error envelope for not-found responses.

P_bottom_up: about 230 production LOC for detail client, detail route, detail
UI, route navigation, and formatting reuse.
T_bottom_up: 0 frontend test LOC. Verification uses build, lint, and manual
browser checks against the local backend.

## Execution Plan

### Manual Acceptance Targets

- Selecting a stored case navigates to `/reconciliation-cases/{case_id}`.
- Directly opening `/reconciliation-cases/{case_id}` calls
  `GET /v1/reconciliation-cases/{case_id}`.
- A successful response renders extraction, payment evidence, decision, and
  timestamps.
- A failed or not-found detail response renders a detail error state without
  breaking browser navigation back to the list.

### Red

- N/A: Milestone 2 frontend phases intentionally do not add frontend tests or
  frontend test tooling. Verification uses build, lint, and manual browser
  checks from [../TESTING.md](../TESTING.md#milestone-2-base-frontend-verification).

### Green

- Add detail DTO types that mirror `ReconciliationCaseResponseV1` from
  [../API.md](../API.md#base-api-schemas), reusing shared DTOs from M2.3.
- Add `getReconciliationCase(caseId: string): Promise<ReconciliationCaseResponseV1>`
  to `frontend/src/api/reconciliation-cases.ts`. It must throw on non-2xx
  responses, preserve `error.code`, `error.message`, and `error.request_id`
  from the canonical error envelope when present, and provide a safe fallback
  message for network or malformed-JSON failures.
- Update the case list UI so each row/card links to
  `/reconciliation-cases/{case_id}` with TanStack Router `Link`.
- Add `frontend/src/routes/reconciliation-cases/$caseId.tsx` as the detail
  route. Keep the route file focused on the TanStack `Route` export and route
  options, matching the M2.3 Fast Refresh-friendly route module pattern.
- Load detail through the route `loader`, read it with
  a route-local component that calls
  `useLoaderData({ from: "/reconciliation-cases/$caseId" })`, and use
  route-level `pendingComponent` and `errorComponent` for
  loading/not-found/network states.
- Add a detail view, with route-local components only if needed, that displays
  external reference, customer reference, extraction evidence, agreed amount,
  actual payment, backend decision status, reason, review flag, confidence, and
  timestamps. Use HeroUI primitives and Tailwind utilities; do not add
  `frontend/src/features` or `frontend/src/ui-kit`.
- Render nullable API fields safely: missing actual payment shows
  `No payment evidence supplied`, null money/currency values use visible
  fallback text, and invalid/empty dates do not crash formatting.
- Add a visible navigation action back to `/reconciliation-cases`.

Pseudo code for selection:

```text
when user selects a case from the list:
    navigate to /reconciliation-cases/{case_id}

route /reconciliation-cases/$caseId:
    pendingComponent renders loading UI
    loader calls getReconciliationCase(caseId)
    component reads useLoaderData({ from: "/reconciliation-cases/$caseId" })
    if not found or network error: errorComponent renders error code/message
    retry/back action calls reset() and router.invalidate() when appropriate
```

### Refactor

- Extract small formatting helpers only if repeated amount/date formatting makes
  the UI harder to read.
- Keep detail-specific extracted pieces route-local under `-components` only
  when the detail route becomes hard to read.

## Setup and Testing in Local Dev

Local commands:

```bash
cd frontend
npm run build
npm run lint
```

Manual check:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Expected manual behavior: load the list, select a stored case, and inspect its
detail route. Paste a known case URL directly into the browser and confirm it
loads the same detail state. Paste an unknown UUID URL, confirm the error state
renders, then use browser Back to return to the working list route.

## What You Can Run After This Phase

With the backend running, the frontend can list stored cases and inspect a case
detail by URL. It still cannot submit a new case.

## Rollout Notes

- Local: verify detail success, direct URL success, failed/not-found direct URL,
  and browser Back returning to the list.
- QA/Staging/Production: N/A until frontend deployment exists.
- Rollback: remove detail client/route/UI changes; list behavior from M2.3
  remains the fallback.

### SaaS Pre-Flight Dispositions

| Concern | Disposition |
| --- | --- |
| Local dev multi-tenant coverage | N/A: M2 uses the non-tenantized Base API. |
| Tenant-aware test cases | N/A: frontend tests are deferred for Milestone 2. |
| Per-environment feature flags | N/A: no frontend deployment or flags in M2.4. |
| Per-tenant production canary | N/A: no production rollout in this phase. |
| Observability verification | N/A: local Vite-only screen with no telemetry. |
| Audit log verification | N/A: detail viewing creates no audit entries. |
| Rate limit / quota verification | N/A: Base API rate limits are deferred. |
| Webhook delivery verification | N/A: no webhooks are emitted. |
| Rollback includes tenant data | N/A: frontend-only change and no tenant data mutation. |
| Kill switch drill | N/A: no deployed flag or kill switch exists yet. |

## Code Generation Instructions

Follow [planning-conventions Code Generation Instructions](../../../.agents/skills/planning-conventions/SKILL.md#code-generation-instructions).
For this phase: keep TypeScript explicit at exported boundaries, avoid
frontend tests/test scripts, avoid router devtools, and keep detail components
route-local while using HeroUI primitives.

## Summary of Changes

- Modify `frontend/src/api/reconciliation-cases.ts` with
  `getReconciliationCase(caseId: string): Promise<ReconciliationCaseResponseV1>`.
- Modify `frontend/src/routes/reconciliation-cases/index.tsx` or its
  route-local list component so each case links to the detail route.
- Add `frontend/src/routes/reconciliation-cases/$caseId.tsx`; optionally add
  `frontend/src/routes/reconciliation-cases/-components/case-detail-view.tsx`
  and shared `-utils/formatters.ts` only when they reduce route file size.
  Regenerate and commit `frontend/src/routeTree.gen.ts` after adding the detail
  route.
- Add detail client behavior.
- Add route-based list/detail navigation.
- Add manual verification coverage for detail loading and error handling.

## Out of Scope

- Create form, editing, review actions, auth, tenant filtering, audit history,
  payment candidate matching, frontend tests, and browser E2E tests.

## Coverage Ledger

| Item | Category | Source | Notes |
| --- | --- | --- | --- |
| Detail endpoint shape | inherited | [../API.md](../API.md#base-api-endpoints) | Uses M1 `GET /v1/reconciliation-cases/{case_id}`. |
| Detail after list | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | Preserves view-before-create order. |
| Detail error handling | inherited | [../TESTING.md](../TESTING.md#milestone-2-base-frontend-verification) | Missing/failed detail must not clear list. |
| Route-based detail navigation | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | M2.3 introduces TanStack Router. |
| M2.3 route foundation exists | assumption | This phase assumptions | Requires route tree, parent route, list route, and API client from M2.3. |
| Backend error envelope exists | assumption | This phase assumptions | Detail client depends on canonical error envelope for route error UI. |
