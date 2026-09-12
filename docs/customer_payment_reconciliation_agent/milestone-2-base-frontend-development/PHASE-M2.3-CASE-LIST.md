# PHASE-M2.3-CASE-LIST.md

## Executive Summary

This phase establishes the Milestone 2 frontend UI and routing foundation, then
builds the first data screen: a stored reconciliation case list backed by
`GET /v1/reconciliation-cases`. It proves the frontend can consume the Base API
before any create form is introduced.

Expected outcome: users can open the local frontend, load stored case summaries,
see loading, empty, success, and error states, and retry failed loads from the
`/reconciliation-cases` route.

Assumptions:

- M2.1 cleaned the scaffold and M2.2 added backend CORS plus API base config.
- The frontend uses React 19, which satisfies HeroUI v3's React requirement.
- The backend Base API is running locally and migrations have been applied.
- The list endpoint returns `ReconciliationCaseListResponseV1`.

P_bottom_up: about 420 production LOC for HeroUI/Tailwind setup, TanStack Router
setup, API types/client, route files, list UI, formatting helpers, and global
CSS cleanup.
T_bottom_up: 0 frontend test LOC. Verification uses build, lint, and manual
browser checks against the local backend.

## Execution Plan

### Manual Acceptance Targets

- A successful `GET /v1/reconciliation-cases` response renders stored case
  summaries from the backend.
- An empty `items` response renders an empty state, not mock data.
- The first request renders a loading state through route-level pending UI.
- A failed request renders an error state with a retry action.
- Retrying re-runs the list route loader without reloading the whole page.
- `/` directs users to `/reconciliation-cases`.

### Red

- N/A: Milestone 2 frontend phases intentionally do not add frontend tests or
  frontend test tooling. Verification uses build, lint, and manual browser
  checks from [../TESTING.md](../TESTING.md#milestone-2-base-frontend-verification).

### Green

- Install `@heroui/react`, `@heroui/styles`, `tailwindcss`, and
  `@tanstack/react-router` from `frontend/`; install dev-time Vite plugins
  `@tailwindcss/vite` and `@tanstack/router-plugin`.
- Preserve the existing Vite React Compiler setup while adding the TanStack
  Router Vite plugin before the React plugin and the Tailwind Vite plugin after
  the React/React Compiler setup. `frontend/vite.config.ts` remains the only
  Vite config file.
- Update `frontend/src/index.css` to import `tailwindcss` first and
  `@heroui/styles` second, then keep only small global body/root defaults.
- Remove `frontend/src/App.css`; app styling should come from HeroUI, Tailwind
  utility classes, and minimal global defaults.
- Add TanStack Router file-based routing with generated and committed
  `frontend/src/routeTree.gen.ts`. Use route files under `frontend/src/routes`;
  do not create `frontend/src/features` or `frontend/src/ui-kit`.
- Replace direct `App` rendering in `frontend/src/main.tsx` with a
  `RouterProvider` created from the generated route tree, and remove
  `frontend/src/App.tsx` if it no longer has a runtime role.
- Add `frontend/src/routes/__root.tsx` as the root route shell. It owns the
  ReconAI header/layout and renders an `Outlet`. HeroUI's setup boundary is the
  global CSS import from `frontend/src/index.css`; do not add a HeroUI provider
  unless the installed HeroUI version's build output requires one.
- Add `frontend/src/routes/index.tsx` and make it redirect to
  `/reconciliation-cases` with TanStack Router navigation. Do not leave a
  second home screen in `App.tsx`.
- Add `frontend/src/api/reconciliation-cases.ts` with DTOs that mirror the
  Base API list response from [../API.md](../API.md#base-api-schemas), plus:
  `listReconciliationCases(): Promise<ReconciliationCaseListResponseV1>`. The
  client reads the M2.2 API base URL helper, throws on non-2xx responses, and
  reads `error.message` from the canonical API error envelope when available.
- Add `frontend/src/routes/reconciliation-cases.tsx` as the route parent for
  list/detail/submit screens and `frontend/src/routes/reconciliation-cases/index.tsx`
  as the case list route.
- Load stored cases through the route `loader`, read them with
  `Route.useLoaderData()`, and use route-level `pendingComponent` and
  `errorComponent` for loading and error states.
- Render status, references, amounts, currency, review flag, and timestamps from
  each `ReconciliationCaseListItemV1`.
- Use HeroUI primitives such as `Table`, `Chip`, `Button`, `Alert`, `Spinner`,
  and `Card` for the route shell, list display, and route states.
- Keep route-specific extracted pieces beside the route in `-components` only
  when the route file becomes hard to read. Expected route-local files, if
  extracted, are `-components/case-list-table.tsx`,
  `-components/case-list-state.tsx`, and `-utils/formatters.ts`.
- Do not add frontend test tooling, frontend test files, or a frontend `test`
  script in this phase.

Pseudo code for loading:

```text
frontend/src/main.tsx:
    createRouter({ routeTree })
    declare TanStack Router module registration for the router type
    render <RouterProvider router={router} /> inside React StrictMode

route /reconciliation-cases:
    pendingComponent renders loading UI
    loader calls listReconciliationCases()
    component reads Route.useLoaderData()
    if items is empty: render empty state
    if items exists: render success(items)
    errorComponent receives { error, reset }
    retry button calls reset() and router.invalidate() to rerun the loader
```

### Refactor

- Do not add React Query, router devtools, global state management, a custom
  `ui-kit`, a `features` folder, or non-HeroUI table libraries.
- Keep route components readable; extract only route-local domain pieces such as
  case table, status chip, or formatting helpers.
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
npm install
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

# Terminal 2, from repo root, create one stored case without adding a seed script
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

Manual success check: open `/reconciliation-cases` and confirm the
`CALL-M2-3` row appears. Manual empty check: run against an empty database.
Manual error/retry check: stop the backend, reload the route, confirm the error
state appears, restart the backend, and use Retry without a full page reload.

## What You Can Run After This Phase

With the backend running at `http://127.0.0.1:8000`, open the Vite frontend and
view stored reconciliation case summaries. If the database has no cases, the UI
shows an empty state rather than mock data.

## Rollout Notes

- Local: verify with a running backend, one stored case, an empty database, and
  a stopped-backend retry scenario.
- QA/Staging/Production: N/A until frontend deployment exists.
- Rollback: remove the M2.3 frontend package/config/route/client changes; no
  backend or database state is affected.

### SaaS Pre-Flight Dispositions

| Concern | Disposition |
| --- | --- |
| Local dev multi-tenant coverage | N/A: M2 uses the non-tenantized Base API. |
| Tenant-aware test cases | N/A: frontend tests are deferred for Milestone 2. |
| Per-environment feature flags | N/A: no frontend deployment or flags in M2.3. |
| Per-tenant production canary | N/A: no production rollout in this phase. |
| Observability verification | N/A: local Vite-only screen with no telemetry. |
| Audit log verification | N/A: list viewing creates no audit entries. |
| Rate limit / quota verification | N/A: Base API rate limits are deferred. |
| Webhook delivery verification | N/A: no webhooks are emitted. |
| Rollback includes tenant data | N/A: frontend-only change and no tenant data mutation. |
| Kill switch drill | N/A: no deployed flag or kill switch exists yet. |

## Code Generation Instructions

Follow [planning-conventions Code Generation Instructions](../../../.agents/skills/planning-conventions/SKILL.md#code-generation-instructions).
For this phase: keep TypeScript explicit at exported boundaries, avoid
frontend tests/test scripts, avoid router devtools, and use HeroUI primitives
instead of local primitive wrappers.

## Summary of Changes

- Modify `frontend/package.json`, `frontend/package-lock.json`, and
  `frontend/vite.config.ts` for HeroUI, Tailwind CSS, and TanStack Router.
- Modify `frontend/src/main.tsx` and `frontend/src/index.css`; remove
  `frontend/src/App.css` and remove `frontend/src/App.tsx` if unused.
- Add `frontend/src/routes/__root.tsx`, `frontend/src/routes/index.tsx`,
  `frontend/src/routes/reconciliation-cases.tsx`,
  `frontend/src/routes/reconciliation-cases/index.tsx`, and generated
  `frontend/src/routeTree.gen.ts`.
- Add `frontend/src/api/reconciliation-cases.ts` with
  `listReconciliationCases(): Promise<ReconciliationCaseListResponseV1>`.
- Add frontend Base API list DTOs and client.
- Add HeroUI, Tailwind CSS, and TanStack Router as the frontend foundation for
  Milestone 2 data screens.
- Add the first real data route for stored case summaries.
- Add manual verification coverage for list behavior.

## Out of Scope

- Detail loading, create form, seed scripts, mock-only screens, auth, tenants,
  dashboard, exports, frontend tests, and browser E2E tests.

## Coverage Ledger

| Item | Category | Source | Notes |
| --- | --- | --- | --- |
| View stored data before create | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | User reordered M2 so list precedes submit. |
| TanStack Router starts in M2.3 | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | List/detail/submit screens use route files. |
| HeroUI and Tailwind start in M2.3 | inherited | [../UI_UX.md](../UI_UX.md#milestone-2-base-frontend-slice) | Avoids a custom `ui-kit`. |
| List response shape | inherited | [../API.md](../API.md#base-api-schemas) | Uses `ReconciliationCaseListResponseV1`. |
| Loading/empty/success/error states | inherited | [../TESTING.md](../TESTING.md#milestone-2-base-frontend-verification) | Required for first data screen. |
| No mock-only screens | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | Empty backend result must show empty UI, not fixtures. |
| M2.1/M2.2 state | assumption | This phase assumptions | Clean shell, CORS, and API base config exist before coding. |
| Backend running for manual checks | assumption | This phase setup | Manual browser checks require the Base API and migrations. |
