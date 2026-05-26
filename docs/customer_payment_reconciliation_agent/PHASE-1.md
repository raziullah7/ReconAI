# PHASE-1.md

## Executive Summary

Phase 1 is the backend-first local development foundation. It keeps the project
small and runnable by using Docker only for PostgreSQL, running the backend
locally with uv, and documenting exact backend commands.

Expected outcome: the developer can start the database, run backend tests, run
the backend health endpoint, and understand that frontend setup is intentionally
deferred.

## Scope

In scope:

- DB-only `compose.yml`.
- `.env.example` with only `DATABASE_URL`.
- Backend settings that require only PostgreSQL.
- Minimal `backend/README.md` with setup/run/test commands.
- Minimal `frontend/README.md` explaining that frontend setup is deferred.
- Focused backend smoke tests.
- Docs reorganization inside this folder.

Out of scope:

- Root Makefile.
- Frontend package setup.
- Vite/React scaffold.
- Frontend tests.
- Redis.
- Ollama.
- Worker process.
- Backend Docker image.
- Frontend Docker image.
- Tenant context.
- Auth.
- Database migrations.
- Reconciliation behavior.

## Execution Plan

### Red

- Keep settings test proving `DATABASE_URL` is the only required runtime URL.
- Keep Compose contract test proving only `postgres` is declared.
- Keep health test as the backend app shell smoke test.

### Green

- Remove Redis, Ollama, backend, frontend, and worker services from Compose.
- Remove deferred settings from the Phase 1 `Settings` class.
- Remove worker/context placeholder files that belong to later phases.
- Remove the root Makefile.
- Remove the premature frontend scaffold.
- Add minimal backend and frontend README files.
- Update docs so current implementation state and future target design are not
  mixed together.

### Refactor

- Keep backend tests small: settings, compose, health.
- Do not add frontend tests until frontend setup becomes a real phase.
- Do not add seed scripts, integration scripts, or placeholder CLIs.

## Local Commands

From the repo root:

```bash
docker compose up -d postgres
```

From the backend folder:

```bash
uv sync
DATABASE_URL=postgresql://reconai:reconai@localhost:5432/reconai uv run fastapi dev --host 127.0.0.1 --port 8000
uv run python -m pytest
uv run mypy app
uv run ruff check .
```

## Acceptance Criteria

- `docker compose config --services` prints only `postgres`.
- Backend settings load with `DATABASE_URL` and do not require Redis.
- `uv run python -m pytest` passes from `backend/`.
- No root Makefile exists.
- `frontend/` contains only deferral documentation and no runnable app setup.
- Docs explain that frontend, Redis, Ollama, workers, and app containers are
  deferred.

## Next Docs Deliverable

Before any Base API implementation starts, complete Milestone 1.1 from
[PLAN.md](PLAN.md): review the Base API contract across [API.md](API.md),
[MODELS.md](MODELS.md), [DEFINITIONS.md](DEFINITIONS.md), [SPEC.md](SPEC.md),
and [TESTING.md](TESTING.md).

The next implementation phase should not call a real LLM. It should accept the
same `AgreementExtractionInputV1` shape that the future LLM adapter will emit,
validate it, compute a backend-owned reconciliation decision, persist the case,
and expose the Base API endpoints.

## Notes For Later Phases

- Frontend setup should be introduced after backend APIs are useful enough to
  display.
- Redis should be introduced in the queue foundation phase.
- Ollama should be introduced in the local AI boundary phase.
- Tenant/request context should be introduced after the base API and persistence
  path are understandable.
- Worker commands should not exist until there is actual worker behavior to run.
