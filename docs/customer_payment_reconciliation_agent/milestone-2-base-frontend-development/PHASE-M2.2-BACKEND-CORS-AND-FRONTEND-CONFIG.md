# PHASE-M2.2-BACKEND-CORS-AND-FRONTEND-CONFIG.md

## Executive Summary

This phase prepares local browser-to-backend connectivity without building data
screens. It adds backend CORS support for the local Vite origin and centralizes
the frontend API base URL so later UI phases can call the Base API directly.

Expected outcome: the backend explicitly allows the local frontend origin, and
the frontend has one typed place to read the Base API base URL.

Assumptions:

- M2.1 has already cleaned the Vite scaffold.
- The frontend calls FastAPI directly with `VITE_RECONAI_API_BASE_URL`; it does
  not use a Vite proxy.
- CORS is local-development configuration only for Milestone 2.

P_bottom_up: about 130 production LOC across backend settings/main wiring,
frontend config, and README/env examples.
T_bottom_up: about 70 test LOC for backend CORS/settings coverage.

## Execution Plan

### Red

- `test_settings_parses_backend_cors_origins`
  - Summary: Proves backend settings expose allowed origins for local frontend
    development.
  - Mocks: Environment override for `BACKEND_CORS_ORIGINS`.
  - Assertions: The settings object returns a list containing
    `http://127.0.0.1:5173` and `http://localhost:5173`.

- `test_cors_allows_local_frontend_origin`
  - Summary: Proves FastAPI responds to browser CORS preflight for the local
    Vite origin.
  - Mocks: FastAPI `TestClient`.
  - Assertions: An `OPTIONS` preflight for `/v1/reconciliation-cases` with the
    configured origin includes `access-control-allow-origin`.

- `frontend_config_builds_with_default_api_base_url`
  - Summary: Proves frontend config compiles without calling the backend.
  - Mocks: None.
  - Assertions: `npm run build` passes and the API base config defaults to
    `http://127.0.0.1:8000` when no env override is provided.

### Green

- Add `BACKEND_CORS_ORIGINS` support to backend settings. The value is a
  comma-separated list and defaults to local Vite origins from
  [../CONFIG.md](../CONFIG.md#backend_cors_origins).
- Register FastAPI `CORSMiddleware` in `create_app` when settings provide at
  least one origin. Use `allow_methods=["GET", "POST", "OPTIONS"]`,
  `allow_headers=["content-type"]`, and `allow_credentials=False` for the
  Milestone 2 local Base API surface.
- Add or update backend tests for settings parsing and local CORS preflight.
- Add `frontend/.env.example` with `VITE_RECONAI_API_BASE_URL`.
- Add `frontend/src/config/api.ts` that exports the normalized Base API URL.
- Update frontend README with the local backend and frontend command sequence.

Required frontend helper shape:

```typescript
const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000'

export function getApiBaseUrl(): string {
  // read import.meta.env.VITE_RECONAI_API_BASE_URL
  // trim trailing slash
  // fall back to DEFAULT_API_BASE_URL
}
```

### Refactor

- Keep API configuration separate from future API client functions.
- Do not add list/detail/form UI in this phase.

## Setup and Testing in Local Dev

Settings and configuration:

```bash
# backend/.env
BACKEND_CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173

# frontend/.env
VITE_RECONAI_API_BASE_URL=http://127.0.0.1:8000
```

Local commands:

```bash
cd backend
uv run python -m pytest
uv run mypy app
uv run ruff check .

cd ../frontend
npm run build
npm run lint
```

## What You Can Run After This Phase

Terminal 1:

```bash
docker compose up -d postgres
cd backend
uv run alembic upgrade head
uv run fastapi dev --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Expected outcome: the frontend shell runs locally and the backend is configured
to accept browser requests from the local Vite origin, even though no data UI is
built yet.

## Rollout Notes

- Local: use the commands above.
- QA/Staging/Production: N/A until the frontend is deployed.
- Rollback: remove the CORS setting and middleware wiring; no database state is
  affected.

## Summary of Changes

- Backend settings and app factory gain local CORS support.
- Frontend gains one API base URL helper and env example.
- READMEs document local two-terminal development.

## Out of Scope

- Vite proxy configuration.
- Case list, case detail, or submit form UI.
- Auth, tenants, CSRF policy, production frontend deployment, and Dockerized
  frontend runtime.

## Coverage Ledger

| Item | Category | Source | Notes |
| --- | --- | --- | --- |
| Backend CORS chosen for M2 connectivity | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | User selected backend CORS over Vite proxy during planning. |
| `BACKEND_CORS_ORIGINS` | new-durable | [../CONFIG.md](../CONFIG.md#backend_cors_origins) | Backend config owner updated before implementation. |
| `VITE_RECONAI_API_BASE_URL` | new-durable | [../CONFIG.md](../CONFIG.md#vite_reconai_api_base_url) | Frontend config owner updated before implementation. |
| No data screens in M2.2 | phase-local | This phase summary | Keeps list/detail/create in later phases. |
