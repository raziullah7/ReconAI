# Repository Map

`AGENTS.md` defines contributor behavior and rules. This file is reference
material: use it to find the right folder, boundary, or local command quickly.

## Top-Level Areas

| Path | Purpose |
| --- | --- |
| `backend/` | FastAPI app, SQLAlchemy/Alembic database code, and pytest tests. |
| `frontend/` | Vite + React frontend source, assets, build, and lint config. |
| `docs/customer_payment_reconciliation_agent/` | Product docs, API contract, architecture notes, and phase plans. |
| `.agents/` | Local agent prompts and reusable workflow skills. |
| `compose.yml` | Local Postgres service only. |

## Backend Reference

| Path | Purpose |
| --- | --- |
| `backend/app/main.py` | FastAPI application entrypoint. |
| `backend/app/routers/` | HTTP route handlers; keep request orchestration here. |
| `backend/app/services/` | Business logic and use-case coordination. |
| `backend/app/repositories/` | Database access and persistence behavior. |
| `backend/app/schemas/` | Pydantic request/response contracts. |
| `backend/app/db/` | SQLAlchemy models, engine/session setup, and DB helpers. |
| `backend/migrations/` | Alembic environment and generated migration versions. |
| `backend/tests/` | Pytest coverage for backend structure and behavior. |

## Frontend Reference

| Path | Purpose |
| --- | --- |
| `frontend/src/` | React application source. |
| `frontend/public/` | Static files served by Vite. |
| `frontend/package.json` | npm scripts and frontend dependencies. |
| `frontend/vite.config.ts` | Vite, React Compiler, router, and CSS plugin setup. |
| `frontend/eslint.config.js` | ESLint configuration. |

## Planning Docs Reference

| Path | Purpose |
| --- | --- |
| `PLAN.md` | Milestone and phase index. |
| `API.md` | Backend API endpoints and schemas. |
| `ARCH.md` | Architecture and layering decisions. |
| `CONFIG.md` | Configuration and environment expectations. |
| `TESTING.md` | Verification strategy by milestone. |
| `UI_UX.md` | Frontend interaction and design direction. |
| `milestone-*/PHASE-*.md` | Concrete implementation plans for each phase. |

## Where To Change Things

- New backend endpoint: start in `backend/app/routers/`, then add schema,
  service, repository, or migration changes only as needed.
- Business rule or reconciliation behavior: start in `backend/app/services/`.
- Database schema or persistence shape: check `backend/app/db/`,
  `backend/app/repositories/`, and `backend/migrations/`.
- Frontend screen or route: start in `frontend/src/`.
- Product or phase planning: update the matching docs under
  `docs/customer_payment_reconciliation_agent/`.
- Agent workflow or prompts: update `.agents/`.

## Command Reference

Backend commands run from `backend/`:

- `uv sync`
- `uv run fastapi dev --host 127.0.0.1 --port 8000`
- `uv run alembic upgrade head`
- `uv run python -m pytest`
- `uv run mypy app`
- `uv run ruff check .`

Frontend commands run from `frontend/`:

- `npm install`
- `npm run dev`
- `npm run build`
- `npm run lint`

Repo root command:

- `docker compose up -d postgres`
