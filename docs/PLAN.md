# ReconAI Implementation Plan

Source spec: `/home/dell/Downloads/customer_payment_reconciliation_agent_dark.pdf`

Source version: 1.1, dated 21 May 2026

## Purpose

ReconAI is a customer payment reconciliation app. It compares what a
customer agreed to pay during a call with what the customer actually paid.

The first useful version should help finance and review users trace a case
from call or transcript intake to extracted payment agreement, payment match,
reconciliation result, review decision, and audit history.

## Core Principle

The LLM helps understand the call, but it does not make the final financial
decision.

The local AI pipeline extracts structured payment agreement data from a
transcript. The backend validates that extracted data. Deterministic backend
rules decide reconciliation outcomes. Humans review unclear, risky, or
ambiguous cases.

## Monorepo Direction

The project is planned as a monorepo with three top-level sections:

- `docs/`: product, architecture, and planning documentation.
- `frontend/`: React/Vite frontend application.
- `backend/`: FastAPI backend API, workers, and service code.

The existing root-level `venv/` can be left alone during planning. When backend
implementation begins, the environment can be recreated or moved into the
backend workflow if that makes the project cleaner.

## Technology Direction

These choices are directional for planning and can be adjusted during
implementation if there is a practical reason.

- Frontend: React, Vite, TypeScript.
- Backend API: FastAPI, Pydantic.
- Database: PostgreSQL.
- Database tooling: SQLAlchemy and Alembic.
- Background jobs: Celery and Redis.
- Local LLM runtime: Ollama.
- Transcription: faster-whisper or whisper.cpp.
- Local orchestration: Docker Compose.
- Future single-server deployment: Nginx in front of frontend/backend services.

## Docker Runtime Direction

The database and AI runtime should run in Docker from the beginning of real
implementation work.

Required Docker services:

- PostgreSQL for persistent application data.
- Redis for background jobs.
- Ollama for the local LLM runtime.

The backend may initially run outside Docker during development and connect to
the Dockerized services. The frontend may initially run outside Docker through
Vite. Full Docker packaging of the backend and frontend can happen later, once
the core app shape is stable.

## Planning Level

This plan is intentionally at the app roadmap level. It defines phases,
deliverables, and verification strategy.

It does not define exact database tables, ORM models, migration files,
indexes, request/response schemas, or final UI layouts. Those details should be
created when each phase is expanded into its own implementation plan.

## Functional Baseline

ReconAI reaches its first functional baseline after **Phase 9: Human Review
Workflow**.

Before that point, the app is still in strict core development. After that
point, the app can run end-to-end and solve the core reconciliation problem.

At the baseline, a finance/review user should be able to:

- Enter or import actual payment records.
- Submit a transcript or call record.
- Extract agreed payment details through the local AI pipeline.
- Validate and store the extracted agreement.
- Match the agreement against actual payment data.
- Receive a deterministic reconciliation result.
- Send unclear, mismatched, or ambiguous cases to review.
- Resolve review cases inside the app.
- See audit history explaining the result.

## Phase Categories

### Core Development / Baseline Build

Phases 1 through 9 are strict development phases. Every phase before the
baseline should directly support the core reconciliation workflow.

The app is not considered functionally complete until Phase 9 is finished.

### Post-Baseline Enhancements

Phases 10 and onward happen after ReconAI can already solve the core problem.
These phases improve usability, reporting, operations, and release readiness.

After the baseline, new phases should be classified as one of:

- Hardening.
- Usability improvement.
- Reporting.
- Operational support.
- Nice-to-have feature.
- Future integration.

## Phase 1: Project Foundation

### Goal

Create the basic project foundation for a from-scratch full-stack app.

### Deliverables

- Confirm the monorepo structure: `docs/`, `frontend/`, and `backend/`.
- Decide the backend project layout and dependency management approach.
- Decide the frontend project layout and package manager approach.
- Define the local Docker Compose direction for PostgreSQL, Redis, and Ollama.
- Define the baseline local development commands.
- Keep GitHub repository creation out of scope for now.

### Testing and Verification

- Verify the expected folders exist.
- Verify Docker service names and ports are documented before implementation.
- Verify the plan explains how backend and frontend will run locally.
- Verify no production deployment assumptions are introduced too early.

## Phase 2: Backend API Foundation

### Goal

Create the first runnable backend surface.

### Deliverables

- FastAPI application scaffold.
- Health check endpoint.
- Typed configuration loading.
- PostgreSQL connection setup.
- Alembic migration setup direction.
- Basic backend test structure.
- Clear separation between API routes, domain logic, data access, and worker
  integration points.

### Testing and Verification

- Backend starts locally.
- Health check returns a successful response.
- Backend can connect to Dockerized PostgreSQL.
- Backend configuration fails clearly when required settings are missing.
- Basic backend tests run successfully.

## Phase 3: Frontend Foundation

### Goal

Create the first runnable frontend surface and connect it to the backend.

### Deliverables

- React/Vite application scaffold.
- TypeScript setup.
- App shell with routing.
- Basic dashboard-style layout direction.
- API client foundation.
- Health/status screen or development-only connection check.

### Testing and Verification

- Frontend starts locally.
- App renders without runtime errors.
- Frontend can call the backend health endpoint.
- Type checking runs.
- Basic frontend tests or smoke checks run.

## Phase 4: Auth, Roles, and App Navigation

### Goal

Add user access control and role-aware app structure.

### Deliverables

- Authentication approach for the first version.
- Role support for Admin, Finance User, Reviewer, and Manager.
- Protected backend route pattern.
- Frontend login/session flow.
- Role-aware navigation and route guards.
- Basic audit awareness for login-sensitive actions.

### Testing and Verification

- Unauthenticated users cannot access protected backend routes.
- Unauthorized roles cannot perform restricted actions.
- Each role sees only the navigation areas intended for that role.
- Session expiration or invalid session behavior is clear to the user.

## Phase 5: Customer and Payment Data

### Goal

Allow users to manage the real payment-side data needed for reconciliation.

### Deliverables

- Customer management capability.
- Manual payment record creation.
- CSV payment import for actual payment records.
- Backend validation for payment inputs.
- Frontend screens for customer and payment workflows.
- Audit entries for payment creation/import actions.

### Testing and Verification

- Users can create and view customers.
- Users can manually add payment records.
- Users can import valid CSV payment data.
- Invalid payment data is rejected with understandable errors.
- Payment data is available for later matching.
- Audit history records payment data changes.

## Phase 6: Call and Transcript Intake

### Goal

Allow users to provide the call-side data needed for reconciliation.

### Deliverables

- Call record creation with customer and call metadata.
- Transcript submission.
- Audio upload path, if included in this phase.
- Initial processing status lifecycle.
- Transcript viewing surface.
- Frontend intake flow for finance/admin users.

### Testing and Verification

- Users can submit a transcript tied to a customer or reference.
- Users can create call records with required metadata.
- Intake failures are visible and recoverable.
- Submitted records appear in the frontend.
- Transcript text remains available for review and audit.

## Phase 7: Background Processing and Local AI

### Goal

Use background jobs and local AI services to extract structured agreement data.

### Deliverables

- Celery/Redis worker setup.
- Job flow for transcription, when audio is available.
- Job flow for local LLM extraction through Ollama.
- Validated structured extraction output.
- Storage of raw extraction context where useful for debugging.
- Processing status updates visible to the frontend.

### Testing and Verification

- Jobs can be queued and processed.
- Failed jobs move to a visible failed state.
- LLM output is validated before business rules use it.
- Low-confidence or incomplete extraction is marked for review.
- The LLM does not directly assign final reconciliation status.

## Phase 8: Matching and Reconciliation Engine

### Goal

Match extracted agreements to actual payments and produce deterministic
reconciliation outcomes.

### Deliverables

- Candidate payment matching using practical signals such as customer, phone
  number, invoice/order reference, currency, date range, and amount similarity.
- Deterministic reconciliation rules.
- Reconciliation case status updates.
- Case detail data for frontend display.
- Backend reasons for each reconciliation result.

### Required Outcomes

- `RECONCILED`
- `UNDERPAID`
- `OVERPAID`
- `PARTIAL_PAYMENT`
- `PAYMENT_NOT_FOUND`
- `MULTIPLE_MATCHES_FOUND`
- `NEEDS_REVIEW`
- `FAILED`

### Testing and Verification

- Rule tests cover each reconciliation outcome.
- Exact matches become `RECONCILED`.
- Paid-below-agreed cases become `UNDERPAID`.
- Paid-above-agreed cases become `OVERPAID`.
- Missing payments become `PAYMENT_NOT_FOUND`.
- Ambiguous matches become `MULTIPLE_MATCHES_FOUND`.
- Low-confidence or unclear cases become `NEEDS_REVIEW`.
- Every result includes an explainable reason.

## Phase 9: Human Review Workflow

### Goal

Let humans resolve cases that cannot be safely finalized automatically.

### Deliverables

- Review queue backend capability.
- Review queue frontend screen.
- Case detail view with transcript, extracted agreement, candidate payments,
  reconciliation status, reason, and audit history.
- Reviewer actions: approve, reject, edit agreed amount when appropriate,
  manually link payment, unlink payment, and add notes.
- Audit entries for review actions.

### Testing and Verification

- Reviewers can open and resolve review cases.
- Non-reviewer roles cannot perform reviewer-only actions.
- Manual payment linking changes the case result in an explainable way.
- Review notes are stored and visible.
- Audit history records who changed what and why.
- End-to-end baseline flow works:
  transcript/call -> extraction -> matching -> reconciliation -> review/audit.

### Baseline Gate

After this phase, ReconAI reaches the first functional baseline.

The app can now solve the main problem: compare the payment agreement from a
call/transcript against actual payment data, produce a status, and route
unclear cases to human review.

## Phase 10: Dashboard, Filters, and Exports

### Goal

Improve visibility and reporting after the baseline workflow exists.

### Deliverables

- Dashboard summary counts.
- Case list filters by status, date, customer, agent, payment method, and
  amount range.
- CSV export for filtered reconciliation results.
- Manager/admin-friendly reporting views.

### Testing and Verification

- Dashboard counts match underlying case data.
- Filters return the expected case set.
- CSV export respects active filters.
- Empty, loading, and error states are clear.
- Larger local seed data remains usable.

## Phase 11: Reprocessing and Operational Safety

### Goal

Make the system safer to operate when extraction, transcription, or
reconciliation needs to be rerun.

### Deliverables

- Re-run transcription where audio exists.
- Re-run LLM extraction.
- Re-run reconciliation after payment or extraction changes.
- Preserve previous results through audit history.
- Basic operational failure visibility.
- Worker retry and failure-handling rules.

### Testing and Verification

- Reprocessing creates traceable new results.
- Previous results are not silently overwritten.
- Failed reprocessing attempts are visible.
- Users can understand which result is current.
- Audit history explains the reprocessing action.

## Phase 12: First Release Readiness

### Goal

Prepare the app for a first serious internal release.

### Deliverables

- End-to-end happy path verification.
- End-to-end review path verification.
- Error path verification.
- Basic security review.
- Basic performance sanity checks.
- Local setup documentation cleanup.
- Deployment-readiness notes.
- Deferred work list.

### Testing and Verification

- Full flow works from intake to audit history.
- Backend tests pass.
- Frontend checks pass.
- Docker services required for local development are documented.
- Known deferred items are listed clearly.
- The team can explain what is baseline, what is hardening, and what is
  future nice-to-have work.

## Deferred Work

These items are intentionally not part of the first baseline:

- Bank statement integrations.
- Payment gateway integrations.
- CRM or call-center integrations.
- Customer notifications by SMS, WhatsApp, or email.
- Advanced analytics and executive dashboards.
- SaaS billing.
- Full multi-tenant packaging.
- PDF report export.
- GitHub repository creation.

## `.agents` Planning Note

The `.agents` folder contains a heavier SaaS-oriented planning system with
PRD, BDD, architecture, specification, phase, review, and coding agents. That
structure may be useful later, but it is heavier than ReconAI needs at this
initial planning stage.

For this project, `docs/PLAN.md` is the main roadmap. Future phase documents
can be created only when we are ready to expand a specific phase into detailed
implementation steps.

Before using `.agents` heavily for ReconAI, it should be adjusted so its output
paths live under `docs/`, SaaS-only assumptions are optional, and unavailable
references such as `metis` or `lint-config` are removed or made optional.

## Planning Rules For Future Phase Documents

When a phase is expanded later, its document should include:

- Objective.
- In scope.
- Out of scope.
- Backend deliverables.
- Frontend deliverables.
- Docker/runtime impact.
- Data concepts touched, without exact table design unless that phase is ready
  for implementation-level schema work.
- API surfaces to consider.
- Background jobs, if any.
- Audit/review impact.
- Testing and verification strategy.
- Risks and open questions.

Phase documents should be created one at a time so the project stays focused
and does not become overwhelming.
