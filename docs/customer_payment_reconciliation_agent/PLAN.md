# PLAN.md

## Goal

Build the customer payment reconciliation agent through small, reversible,
learning-friendly milestones. Each milestone should introduce one understandable
piece of the system, leave the project runnable, and pass document review before
implementation starts.

## Current Foundation Rule

For the early phases, Docker is only for PostgreSQL. The backend runs locally
with uv. The frontend starts in Milestone 2 as a local Vite app only; frontend
Docker, Redis, Ollama, and workers remain deferred until a phase needs them.

## Development Shape

The first useful product loop is intentionally small:

1. A caller provides an LLM-shaped agreement extraction payload.
2. The backend validates that payload.
3. The backend compares it with an actual payment input or stored payment later.
4. The backend owns the final reconciliation decision.
5. The frontend displays the backend result after the Base API is stable.

The real LLM integration is not part of the Base API milestone. Mock data, seed
data, and tests must use the same `AgreementExtractionInputV1` shape that the
future LLM adapter will emit.

## Guiding Principles

- One subsystem per phase whenever possible.
- Backend first; frontend later.
- Every phase states what the user can run after it.
- Prefer focused tests that prove behavior, not broad folder-shape tests.
- Do not add future infrastructure to the current phase.
- Keep docs, config, tests, and commands understandable before adding domain
  behavior.
- Use TDD for behavior changes, but do not create broad meta tests that only
  assert folder shape.
- The LLM proposes extracted facts; backend validation and deterministic rules
  decide the final status.

## Planning And Review Gates

Every non-trivial milestone follows this order:

1. Designer agents update the owning docs only:
   - `@api-designer` for request and response payloads in [API.md](API.md).
   - `@data-modeler` for persistence shape in [MODELS.md](MODELS.md).
   - `@interface-designer` for services, repositories, and pure functions in
     [DEFINITIONS.md](DEFINITIONS.md).
   - `@test-strategist` for test scope in [TESTING.md](TESTING.md).
   - `@plan-designer` or `@phase-designer` for milestone and phase sequencing.
2. Reviewer agents check the docs before code:
   - `@doc-reviewer` reviews PLAN/PHASE clarity, consistency, and drift.
   - `@spec-reviewer` reviews SPEC/API/MODELS/DEFINITIONS/TESTING consistency.
   - `@phase-reviewer` reviews each `PHASE-{N}.md` before implementation.
3. The user approves the reviewed phase plan.
4. `@phase-coder` implements only the accepted phase plan.

`@phase-coder` treats the phase plan as its sole source of truth, so phase plans
must include exact files, function names, tests, local commands, and out-of-scope
items.

## Clarification Gates

These gates remain before later domain phases are finalized:

- Gate A: extraction confidence threshold. This must be resolved in M1.1 before validation or decision code starts.
- Gate B: tenant mode and tenant switching behavior.
- Gate C: notification scope.
- Gate D: local LLM model and hardware expectations.
- Gate E: CSV import columns.
- Gate F: retention periods.
- Gate G: Finance User review authority.

## Milestone Overview

| Milestone | Title | Main Outcome | Review Before Code | Can Run Afterward |
| --- | --- | --- | --- | --- |
| 0 | Current Foundation | DB-only Compose, uv backend env, minimal READMEs, current docs | Completed foundation summary | backend pytest |
| 1 | Base API Development | Create, list, and fetch persisted reconciliation cases from LLM-shaped input | `@spec-reviewer`, `@doc-reviewer`, `@phase-reviewer` | backend API tests and local `/v1/reconciliation-cases` |
| 2 | Base Frontend Development | First UI views stored Base API data before adding create flows | `@doc-reviewer`, `@phase-reviewer` | frontend dev server against Base API |
| 3 | LLM Integration | Local LLM adapter emits `AgreementExtractionInputV1` for the same backend path | `@spec-reviewer`, `@phase-reviewer` | mocked and local LLM extraction checks |
| 4 | Vertical Expansion | Auth, tenants, customers, payments, workers, review, dashboard, and exports in slices | reviewer matched to each slice | full-stack checks for each slice |

## Milestone 0: Current Foundation

Purpose: make local backend development understandable before domain code lands.

Delivered scope:

- `compose.yml` declares PostgreSQL only.
- `backend/.env.example` contains the local PostgreSQL URL only.
- `backend/README.md` documents uv setup, backend run, health check, and tests.
- `frontend/README.md` documents that frontend setup is deferred.
- Backend tests are limited to settings, Compose contract, and health endpoint.

No frontend app, Redis, Ollama, worker, Makefile, tenant context, auth, database
migrations, or reconciliation behavior belongs in this milestone.


## Milestone 1: Base API Development

Purpose: make the backend useful enough for a later frontend while keeping the
LLM mocked or manually supplied.

Detailed phase plans live in
[milestone-1-base-api-development/](milestone-1-base-api-development/).

| Order | Phase | Main Outcome |
| --- | --- | --- |
| 1 | [M1.1 Contract Docs And Review](milestone-1-base-api-development/PHASE-M1.1-CONTRACT-DOCS-AND-REVIEW.md) | Freeze owner docs and resolve Gate A. |
| 2 | [M1.2 Database Toolkit And Minimal Case Storage](milestone-1-base-api-development/PHASE-M1.2-DATABASE-TOOLKIT-AND-MINIMAL-CASE-STORAGE.md) | Add DB tooling, migration, table, and repository. |
| 3 | [M1.3 Validation And Reconciliation Core](milestone-1-base-api-development/PHASE-M1.3-VALIDATION-AND-RECONCILIATION-CORE.md) | Add validation, decisions, and service behavior. |
| 4 | [M1.4 Backend Layer Structure Alignment](milestone-1-base-api-development/PHASE-M1.4-BACKEND-LAYER-STRUCTURE-ALIGNMENT.md) | Align backend folders around router, service, repository, domain, schema, and dependency boundaries before HTTP endpoints. |
| 5 | [M1.5 Base API Endpoints](milestone-1-base-api-development/PHASE-M1.5-BASE-API-ENDPOINTS.md) | Expose create/list/detail endpoints. |

Milestone 1 boundaries:

- `EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD` is `0.80`.
- Base API paths are local and non-tenantized.
- List pagination uses `limit` and `offset` for Milestone 1 only.
- `MULTIPLE_MATCHES_FOUND` is deferred until payment-ledger matching exists.
- Auth, tenant context, idempotency records, cursor pagination, Redis, Ollama,
  workers, frontend, CSV import, and payment-ledger matching remain out of
  scope.

## Milestone 2: Base Frontend Development

Purpose: add the first frontend after Milestone 1 gives it real stored case data
to view. Milestone 2 views existing Base API data before it introduces the
create form.

Detailed phase plans live in
[milestone-2-base-frontend-development/](milestone-2-base-frontend-development/).

| Order | Phase | Main Outcome |
| --- | --- | --- |
| 1 | [M2.1 Frontend Scaffold Cleanup](milestone-2-base-frontend-development/PHASE-M2.1-FRONTEND-SCAFFOLD-CLEANUP.md) | Replace the starter Vite UI with a minimal ReconAI shell and local README. |
| 2 | [M2.2 Backend CORS And Frontend Config](milestone-2-base-frontend-development/PHASE-M2.2-BACKEND-CORS-AND-FRONTEND-CONFIG.md) | Allow the browser frontend to call the local FastAPI backend and centralize the frontend API base URL. |
| 3 | [M2.3 Case List](milestone-2-base-frontend-development/PHASE-M2.3-CASE-LIST.md) | Display stored reconciliation case summaries from the Base API. |
| 4 | [M2.4 Case Detail](milestone-2-base-frontend-development/PHASE-M2.4-CASE-DETAIL.md) | Display one stored reconciliation case detail from the Base API. |
| 5 | [M2.5 Reconciliation Submit And Result](milestone-2-base-frontend-development/PHASE-M2.5-RECONCILIATION-SUBMIT-AND-RESULT.md) | Submit `ReconciliationCaseCreateRequestV1` and display the backend decision response. |

Milestone 2 boundaries:

- The frontend consumes only the Milestone 1 Base API.
- Case list and detail come before create so users can inspect stored data
  before adding new cases.
- Backend CORS is introduced only for local Vite-to-FastAPI development.
- No mock-only screens are allowed; every data screen must call the current
  backend contract.
- Frontend Docker, Redis, Ollama, workers, auth, tenants, dashboards, exports,
  CSV import, and payment-ledger matching remain out of scope.

## Milestone 3: LLM Integration

Purpose: replace manually supplied extraction data with a local LLM extraction
adapter while preserving the same backend contract.

Scope:

- Prompt and parser that produce `AgreementExtractionInputV1`.
- Raw model output retained for audit/debugging.
- Validation failures routed to backend review-safe statuses.
- Optional Ollama service only when this milestone actually needs it.

Out of scope:

- Letting the LLM decide reconciliation status.
- Adding workers before processing needs asynchronous runtime.

## Milestone 4: Vertical Expansion

After the base loop works, extend the product in reviewed slices:

- Tenant and request context.
- Authentication shell.
- Customers and payment ledger.
- Payment matching against stored payments.
- Review workflow and audit history.
- Redis queue and worker runtime.
- Dashboard, filters, and exports.
- Hardening, observability, rollback, and release checks.

Each slice gets its own phase plan and review gate before code.

## Reference File Index

- Product intent: [PRD.md](PRD.md)
- Business scenarios: [BDD.md](BDD.md)
- Architecture: [ARCH.md](ARCH.md)
- Technical design: [SPEC.md](SPEC.md)
- API contracts: [API.md](API.md)
- Data model: [MODELS.md](MODELS.md)
- Interfaces: [DEFINITIONS.md](DEFINITIONS.md)
- Configuration: [CONFIG.md](CONFIG.md)
- UI/UX: [UI_UX.md](UI_UX.md)
- Testing: [TESTING.md](TESTING.md)
