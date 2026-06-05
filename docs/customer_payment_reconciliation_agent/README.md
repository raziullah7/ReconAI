# Customer Payment Reconciliation Agent

This folder contains the planning documents for ReconAI. The documents describe
both the full product direction and the small implementation phases used to get
there. The current implementation is moving from the completed backend-first
Base API into local Vite frontend phases. Docker still runs only PostgreSQL.

## Current Status

- Current merge state: Milestone 1 Base API is merged; Milestone 2 frontend
  planning is beginning from the stable Base API.
- Docker scope: PostgreSQL only.
- Backend scope: FastAPI app shell, database toolkit, Alembic migration,
  validation and decision core, service/repository layers, and Base API
  create/list/detail endpoints.
- Frontend scope: Milestone 2 introduces a local Vite app in small reviewed
  phases, starting with scaffold cleanup before any API screens.
- Deferred services: Redis, Ollama, background workers, backend Docker image,
  frontend Docker image, transcription, payment-ledger matching, review
  workflow, dashboard, and exports.

## Delivery Workflow

Use a docs-first workflow for every meaningful feature slice:

1. Update the contract docs that own the decision.
2. Review the docs with the matching reviewer agent before code starts.
3. Resolve review findings in the docs.
4. Generate or update the next `PHASE-{N}.md` plan.
5. Review the phase plan with `@phase-reviewer`.
6. Invoke `@phase-coder` only after the phase plan is accepted.

The owning files are:

- [API.md](API.md) owns request and response payloads.
- [MODELS.md](MODELS.md) owns persistence shapes.
- [DEFINITIONS.md](DEFINITIONS.md) owns service, repository, and pure function
  interfaces.
- [TESTING.md](TESTING.md) owns test scope by milestone.
- [PLAN.md](PLAN.md) owns sequence, review gates, and phase boundaries.
- [milestone-1-base-api-development/](milestone-1-base-api-development/) owns the detailed Milestone 1 phase plans.
- [milestone-2-base-frontend-development/](milestone-2-base-frontend-development/) owns the detailed Milestone 2 phase plans.

## Milestone Map

| Milestone | Name | Purpose |
| --- | --- | --- |
| 0 | Current Foundation | Keep local backend setup small and understandable. |
| 1 | Base API Development | Accept LLM-shaped extraction input, persist a case, and return deterministic reconciliation results. |
| 2 | Base Frontend Development | View stored Base API data before adding the create flow. |
| 3 | LLM Integration | Replace mocked extraction input with a real local LLM adapter that emits the same schema. |
| 4 | Vertical Expansion | Add auth, tenant context, payments, review workflow, workers, dashboard, and exports in reviewed slices. |

## How To Run The Current App

From the repo root, start the database:

```bash
docker compose up -d postgres
```

From the backend folder, install and run the backend:

```bash
cd backend
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run fastapi dev --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Base API smoke check:

```bash
curl http://127.0.0.1:8000/v1/reconciliation-cases
```

Backend checks:

```bash
cd backend
uv run python -m pytest
uv run mypy app
uv run ruff check .
```

Frontend commands are introduced by Milestone 2. Until M2.1 is implemented,
treat the frontend as planning-only in committed project history.

## Recommended Reading Order

1. [README.md](README.md) - where to start and what is implemented now.
2. [PLAN.md](PLAN.md) - milestone sequence and review gates.
3. [milestone-1-base-api-development/](milestone-1-base-api-development/) - detailed Milestone 1 phase plans.
4. [milestone-2-base-frontend-development/](milestone-2-base-frontend-development/) - detailed Milestone 2 phase plans.
5. [API.md](API.md) - Base API contract and target endpoint contracts.
6. [MODELS.md](MODELS.md) - Base persistence shape and target data model.
7. [DEFINITIONS.md](DEFINITIONS.md) - function and service contracts.
8. [TESTING.md](TESTING.md) - how much testing each milestone should carry.
9. Product and design references as needed: [PRD.md](PRD.md),
   [BDD.md](BDD.md), [ARCH.md](ARCH.md), [SPEC.md](SPEC.md),
   [CONFIG.md](CONFIG.md), and [UI_UX.md](UI_UX.md).

## Document Map

| Document | Purpose | Implementation Status |
| --- | --- | --- |
| [PRD.md](PRD.md) | Product goals, users, requirements, non-goals | Target product direction |
| [BDD.md](BDD.md) | Business-readable scenarios | Target behavior |
| [ARCH.md](ARCH.md) | Architecture direction and tradeoffs | Target architecture |
| [SPEC.md](SPEC.md) | Technical design | Target design, not fully implemented |
| [PLAN.md](PLAN.md) | Milestone sequence and review gates | Milestone sequence and review gates |
| [milestone-1-base-api-development/](milestone-1-base-api-development/) | Milestone 1 phase plans | Implemented phase history for M1 |
| [milestone-2-base-frontend-development/](milestone-2-base-frontend-development/) | Milestone 2 phase plans | Planned frontend phases |
| [CONFIG.md](CONFIG.md) | Runtime settings and feature flags | Split into current and deferred |
| [TESTING.md](TESTING.md) | Test strategy by phase maturity | Milestone 1 implemented; Milestone 2 planned |
| [API.md](API.md) | Base API and target endpoint contracts | Base API implemented; target contracts documented |
| [MODELS.md](MODELS.md) | Base persistence shape and target model | Base persistence model implemented; target model documented |
| [DEFINITIONS.md](DEFINITIONS.md) | Planned interfaces | Base interfaces implemented; target interfaces documented |
| [UI_UX.md](UI_UX.md) | Planned product screens and flows | Later-phase contracts |

## Folder Rules

- Keep target reference docs at the root so links remain easy to follow.
- Use milestone folders for detailed phase plans.
- Use `PLAN.md` for milestone sequencing and review gates only.
- Use `PHASE-M{N}.{X}-*.md` files inside milestone folders for one phase at a time.
- Add frontend behavior only through the Milestone 2 phase plans, starting with
  scaffold cleanup before data screens.
- Do not move Redis, Ollama, workers, or Dockerized apps into an early phase
  just because the final product will need them.
- Every phase should end with a small set of commands the developer can run.
