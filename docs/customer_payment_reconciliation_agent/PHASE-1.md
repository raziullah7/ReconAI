# PHASE-1.md

## Executive Summary

Phase 1 creates the runnable project foundation for ReconAI without
shipping reconciliation behavior. It plans the backend FastAPI scaffold,
frontend Vite shell, typed settings loader, health endpoint, ambient context
stubs, uv-managed backend project environment, Docker Compose skeleton,
worker placeholders, and first smoke tests from [PLAN.md Phase 1][plan-p1].

Expected outcome: a later implementer can create the initial backend,
frontend, and compose runtime, run health checks locally, and prove the app
shell can render while domain modules remain empty.

Assumptions:

- The output filename is `PHASE-1.md` because the user requested that
  repo-local naming.
- The current codebase has only `backend/.gitkeep` and `frontend/.gitkeep`,
  so this phase plans scaffold creation rather than modifying an existing
  runtime.
- Tenant coverage is fixture-level only because Phase 1 has no tenant-scoped
  persistence or user-facing tenant switching.
- The backend virtual environment is `backend/.venv`, created by uv for
  local development and never committed. Containers recreate their own
  environment from `backend/pyproject.toml` and `backend/uv.lock`.

Relation to the overall plan: this phase freezes the runtime shape that later
schema, auth, intake, worker, and reconciliation phases build on. Domain
modules remain intentionally empty until their owning phases.

Sizing estimate:

- `P_bottom_up`: 430 production LOC.
- `T_bottom_up`: 240 test LOC.
- Parent contract: 300-450 production LOC and 180-280 test LOC, archetype
  `contract freeze / stubs only`; the estimate is within band.

Production sizing basis:

| Artifact | Heuristic row | Tier | LOC |
| --- | --- | --- | --- |
| Backend app factory and health route | HTTP endpoint | Small | 30 |
| Typed settings object and loader | Config loader / typed runtime-config object | Typical | 60 |
| Ambient context and port stubs | Context models / protocol stubs | Small x 6 | 100 |
| Backend uv project, lockfile, ignore, and dev entrypoint | Project metadata / setup | Typical | 60 |
| Frontend Vite shell and health surface | Pure helper function | Typical | 60 |
| Frontend health client | HTTP client | Small | 80 |
| Compose and worker placeholder wiring | Config loader / typed runtime-config object | Small | 40 |

Test sizing basis:

| Test group | Heuristic row | Tier | LOC |
| --- | --- | --- | --- |
| Backend health and config tests | Endpoint smoke / unit with docstring | Mixed | 65 |
| Backend context, uv project, and compose checks | Unit with docstring | Mixed | 80 |
| Frontend shell render test | Unit with docstring and jsdom setup | Typical | 45 |
| Frontend health client test | Unit with mocked fetch and docstring | Typical | 50 |

## FastAPI and uv Research Basis

Phase 1 follows current project-structure guidance from official FastAPI and
uv documentation:

- FastAPI documents uv as a supported way to create the project virtual
  environment; `uv venv` creates `.venv` by default, and `.venv` is the
  conventional environment directory.
  [FastAPI virtual environments](https://fastapi.tiangolo.com/virtual-environments/)
- uv project commands create and manage `.venv` and `uv.lock` for a project,
  and `uv run` executes commands in the synchronized project environment.
  [uv projects](https://docs.astral.sh/uv/guides/projects/)
- FastAPI recommends larger applications move beyond a single file with an
  `app/` package, `main.py`, dependencies, routers, and an explicit
  `[tool.fastapi]` entrypoint in `pyproject.toml`.
  [FastAPI bigger applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- FastAPI settings guidance uses `pydantic-settings`, dependency injection,
  and `lru_cache` so settings are not rebuilt for every request.
  [FastAPI settings](https://fastapi.tiangolo.com/advanced/settings/)
- FastAPI testing guidance uses `fastapi.testclient.TestClient` with pytest
  test functions.
  [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- FastAPI CLI uses `fastapi dev` for development and `fastapi run` for
  production/container execution, with the `pyproject.toml` entrypoint
  preferred over repeating command-line paths.
  [FastAPI CLI](https://fastapi.tiangolo.com/fastapi-cli/)
- FastAPI container guidance recommends custom images and notes that uv-based
  projects should follow uv Docker guidance instead of copying local virtual
  environments into images.
  [FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/)

## Delivery Goals

| ID | Source | Goal |
| --- | --- | --- |
| P1 | [PLAN.md Phase 1][plan-p1] | Create a runnable monorepo foundation without reconciliation behavior. |
| P2 | [PLAN.md Phase 1 Red][plan-p1] | Add failing backend health and config tests first. |
| P3 | [PLAN.md Phase 1 Red][plan-p1] | Add failing frontend shell and health-client smoke tests first. |
| P4 | [PLAN.md Phase 1 Red][plan-p1] | Add practical compose/config validation checks. |
| P5 | [PLAN.md Phase 1 Green][plan-p1] | Add backend app skeleton, settings loader, health endpoint, and dev entrypoint. |
| P6 | [PLAN.md Phase 1 Green][plan-p1] | Add frontend Vite shell with backend health status. |
| P7 | [PLAN.md Phase 1 Green][plan-p1] | Add Docker Compose services for PostgreSQL, Redis, Ollama, backend, frontend, and worker placeholders. |
| P8 | [PLAN.md Phase 1 Refactor][plan-p1] | Normalize local commands, env naming, and package layout while keeping domain modules empty. |
| P9 | [PLAN.md Phase 1 Mapping][plan-p1] | Provide stubs for `TenantContext`, `UserContext`, `RequestContext`, `Clock`, `Logger`, and `Tracer`. |
| P10 | [PLAN.md Phase 1 Mapping][plan-p1] | Cover only the health endpoint and Login/Dashboard shell skeletons. |
| S1 | This phase plan | Document executable TDD steps, rollout checks, and coverage ledger for Phase 1. |

## Execution Plan

### Red

Create these tests before production implementation.

#### Backend Health Test

File: [backend/tests/test_health.py](../../backend/tests/test_health.py)
(new).

Test signature:

```python
def test_health_endpoint_returns_ok(client: TestClient) -> None:
    """Verifies that the health endpoint reports a usable app shell.

    Mocks:
        client: Uses the FastAPI test client so the route is exercised
            through the ASGI app without opening a network socket.

    Assertions:
        - Response status is 200 so compose and probes have a stable
          readiness target.
        - Response body contains `status`, `service`, and `version` so
          callers can identify the running service.
        - Response body does not include reconciliation, tenant data, or
          worker state because Phase 1 is scaffold-only.
    """
```

Expected initial failure: `backend.app.main` or `/health` is missing.

#### Backend Settings Test

File: [backend/tests/test_config.py](../../backend/tests/test_config.py)
(new).

Test signature:

```python
def test_settings_require_database_and_redis_urls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifies that required infrastructure URLs fail fast when absent.

    Mocks:
        monkeypatch: Clears environment variables so settings validation is
            isolated from the developer machine.

    Assertions:
        - `load_settings.cache_clear()` is called before and after
          environment mutation so cached settings cannot leak between tests.
        - Missing `DATABASE_URL` raises a validation error.
        - Missing `REDIS_URL` raises a validation error.
        - Error text names the missing setting to keep local setup
          actionable.
    """
```

Expected initial failure: no settings loader exists.

#### Backend Tenant Stub Test

File: [backend/tests/test_context.py](../../backend/tests/test_context.py)
(new).

Test signature:

```python
def test_context_stubs_keep_tenant_values_distinct() -> None:
    """Verifies that Phase 1 context stubs can represent two tenants.

    Assertions:
        - Tenant A and Tenant B have distinct `tenant_id`,
          `tenant_status`, `locale`, and `currency_default` values.
        - User contexts preserve `user_id`, `tenant_id`, `role`, and
          `permissions` values.
        - Request contexts preserve `tenant`, optional `user`, `request_id`,
          and optional `idempotency_key` values without shared mutable state.
        - No persistence or tenant switching behavior is implied by the
          stubs.
    """
```

Expected initial failure: context stubs do not exist.

#### Compose Skeleton Test

File: [backend/tests/test_compose_contract.py](../../backend/tests/test_compose_contract.py)
(new).

Test signature:

```python
def test_compose_declares_foundation_services() -> None:
    """Verifies that compose declares the services Phase 1 promises.

    Assertions:
        - `postgres`, `redis`, `ollama`, `backend`, `frontend`, and
          `worker` services are present.
        - Stateful services use named volumes so local data is not tied to
          a container ID.
        - Worker service starts as a placeholder and does not run domain
          processing yet.
    """
```

Expected initial failure: no compose file exists.

#### Frontend Shell Test

File: [frontend/src/App.test.tsx](../../frontend/src/App.test.tsx)
(new).

Test signature:

```typescript
it("test_frontend_app_renders_shell", () => {
  /**
   * Verifies that the Vite app renders the initial operator shell.
   *
   * Mocks:
   * fetchHealth: Replaces the backend health client so the component test
   *   does not depend on a running backend.
   *
   * Assertions:
   * - The shell exposes Login and Dashboard skeleton regions.
   * - The health status surface is present.
   * - No customer, payment, call, or reconciliation workflows render in
   *   Phase 1.
   */
});
```

Expected initial failure: no Vite app exists.

#### Frontend Health Client Test

File: [frontend/src/api/health.test.ts](../../frontend/src/api/health.test.ts)
(new).

Test signature:

```typescript
it("test_frontend_health_client_handles_ok_response", async () => {
  /**
   * Verifies that the health client parses a successful backend response.
   *
   * Mocks:
   * fetch: Returns a synthetic 200 response from `/health` so the client
   *   contract is tested without network access.
   *
   * Assertions:
   * - The client calls the configured backend base URL.
   * - The returned health object includes `status`, `service`, and
   *   `version`.
   * - The client does not attach auth or tenant headers in Phase 1.
   */
});
```

Expected initial failure: no frontend health client exists.

#### Backend uv Project Structure Test

File: [backend/tests/test_project_structure.py](../../backend/tests/test_project_structure.py)
(new).

Test signature:

```python
def test_backend_uses_uv_project_structure() -> None:
    """Verifies that backend setup uses uv without committing `.venv`.

    Assertions:
        - `backend/pyproject.toml` declares project metadata, runtime
          dependencies, dev dependency group, and `[tool.fastapi]`
          entrypoint `app.main:app`.
        - `backend/uv.lock` is present as the reproducible dependency lock.
        - `.gitignore` ignores `backend/.venv/` so the local environment
          remains untracked.
        - `backend/app/api`, `backend/app/core`, and
          `backend/app/features` are Python packages reserved for later
          routers and feature modules.
        - No `requirements.txt` is introduced for Phase 1.
    """
```

Expected initial failure: uv project files and ignore rules do not exist.

### Green

Implement only enough code to satisfy the Red tests.

#### Backend Runtime Scaffold

Files:

- [.gitignore](../../.gitignore) (new).
- [backend/pyproject.toml](../../backend/pyproject.toml) (new).
- [backend/uv.lock](../../backend/uv.lock) (new).
- [backend/app/main.py](../../backend/app/main.py) (new).
- [backend/app/__init__.py](../../backend/app/__init__.py) (new).
- [backend/app/api/__init__.py](../../backend/app/api/__init__.py) (new).
- [backend/app/core/__init__.py](../../backend/app/core/__init__.py) (new).
- [backend/app/core/config.py](../../backend/app/core/config.py) (new).
- [backend/app/core/context.py](../../backend/app/core/context.py) (new).
- [backend/app/features/__init__.py](../../backend/app/features/__init__.py)
  (new).

Planned signatures and docstrings:

```python
class Settings(BaseSettings):
    """Stores runtime settings required by the Phase 1 app shell.

    What: Validates infrastructure URLs, feature-flag defaults, storage
        location, and local runtime endpoints from environment variables.
    Why: The app must fail fast when required local dependencies are not
        configured, before later phases add domain behavior.

    States / Side Effects:
        Reads environment variables using the configured settings source.
    """
```

```python
@lru_cache
def load_settings() -> Settings:
    """Load and cache validated runtime settings.

    What: Builds the typed settings object once per process.
    Why: FastAPI dependencies and tests need a single settings entrypoint
        that can be overridden without global ad hoc parsing.

    Returns:
        Validated runtime configuration for the app shell.

    Raises:
        ValidationError: If required environment values are missing or
            malformed.

    States / Side Effects:
        Reads environment variables and caches the resulting settings.
    """
```

```python
def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the FastAPI application for the Phase 1 shell.

    What: Registers metadata, dependency overrides, and the health route.
    Why: Tests and development commands need a repeatable app factory before
        domain routers exist.

    Args:
        settings: Optional prebuilt settings for tests. Defaults to None,
            which loads settings from the environment.

    Returns:
        Configured application with only foundation routes.

    States / Side Effects:
        Reads cached settings when no explicit settings object is supplied.
    """
```

```python
async def health(
    settings: Annotated[Settings, Depends(load_settings)],
) -> dict[str, str]:
    """Return readiness metadata for the app shell.

    What: Reports a small health payload for local probes and the frontend.
    Why: Phase 1 needs a stable integration point before domain APIs ship.

    Args:
        settings: Validated runtime settings injected by FastAPI.

    Returns:
        Service name, version, and status metadata.
    """
```

```python
@dataclass(frozen=True)
class TenantContext:
    """Carry tenant identity through future request boundaries.

    What: Stores the Phase 1 tenant fields named by the interface contract.
    Why: Later request, repository, and worker code need a stable context
        shape before tenant-scoped persistence exists.

    Args:
        tenant_id: Internal tenant identifier, mapped from `tenantId` in
            the planning contract.
        tenant_status: Operational tenant state, mapped from
            `tenantStatus`.
        locale: Tenant locale used by later formatting logic.
        currency_default: Default tenant currency, mapped from
            `currencyDefault`.
    """

    tenant_id: str
    tenant_status: str
    locale: str
    currency_default: str
```

```python
@dataclass(frozen=True)
class UserContext:
    """Carry authenticated user identity for future authorization.

    What: Stores user, tenant, role, and permission values from the
        interface contract.
    Why: Phase 1 freezes the request context shape without implementing
        authentication or RBAC behavior.

    Args:
        user_id: Internal user identifier, mapped from `userId`.
        tenant_id: Tenant identifier associated with the user.
        role: Role name from the planned role set.
        permissions: Immutable permission names granted to the user.
    """

    user_id: str
    tenant_id: str
    role: str
    permissions: frozenset[str]
```

```python
@dataclass(frozen=True)
class RequestContext:
    """Group tenant, user, request ID, and idempotency context.

    What: Carries the ambient context fields named by the interface
        contract in one immutable object.
    Why: Later services receive context explicitly instead of reading
        global state.

    Args:
        tenant: Tenant context resolved for the request.
        user: Optional user context. Defaults to None for unauthenticated
            foundation paths such as health checks.
        request_id: Correlation identifier, mapped from `requestId`.
        idempotency_key: Optional mutating-request idempotency key. Defaults
            to None because Phase 1 has no mutating API.
    """

    tenant: TenantContext
    user: UserContext | None
    request_id: str
    idempotency_key: str | None = None
```

```python
class Clock(Protocol):
    """Define the injected time source used by later services."""

    def now(self) -> datetime:
        """Return the current timezone-aware timestamp."""
```

```python
class Logger(Protocol):
    """Define the structured logging port used by later services."""
```

```python
class Tracer(Protocol):
    """Define the trace-span port used by later services."""
```

Pseudo code:

```text
create backend package layout with app/api, app/core, and app/features packages
define pyproject project metadata, dependency groups, and [tool.fastapi]
    entrypoint = "app.main:app"
create backend/uv.lock from the backend pyproject dependency set
add backend/.venv/ to .gitignore and do not plan it as a tracked file
define Settings with DATABASE_URL, REDIS_URL, OLLAMA_BASE_URL,
    STORAGE_ROOT, feature flags, and worker concurrency fields
leave RECONAI_LLM_MODEL, TRANSCRIPTION_BACKEND, and
    EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD for later owning phases
validate DATABASE_URL starts with postgresql
validate REDIS_URL starts with redis
create FastAPI app with title "ReconAI"
override load_settings when create_app receives explicit test settings
register GET /health
return {"status": "ok", "service": "reconai-backend", "version": app version}
use `uv run fastapi dev` locally and `uv run fastapi run` for container/prod
define frozen context dataclasses and minimal Protocol ports
leave domain feature packages absent or empty
```

#### Frontend Runtime Scaffold

Files:

- [frontend/package.json](../../frontend/package.json) (new).
- [frontend/index.html](../../frontend/index.html) (new).
- [frontend/vite.config.ts](../../frontend/vite.config.ts) (new).
- [frontend/src/main.tsx](../../frontend/src/main.tsx) (new).
- [frontend/src/App.tsx](../../frontend/src/App.tsx) (new).
- [frontend/src/api/health.ts](../../frontend/src/api/health.ts) (new).

Planned signatures and docstrings:

```typescript
export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}
```

```typescript
/**
 * Fetch backend health metadata.
 *
 * What: Calls the Phase 1 backend health endpoint and parses the JSON
 * response.
 * Why: The frontend shell needs a small integration check before
 * authenticated tenant workflows exist.
 *
 * @param baseUrl - Backend origin without a trailing slash.
 * @param signal - Optional abort signal. Defaults to undefined.
 * @returns Parsed backend health metadata.
 * @throws {Error} When the backend returns a non-OK response.
 */
export async function fetchHealth(
  baseUrl: string,
  signal?: AbortSignal
): Promise<HealthResponse> {
}
```

```typescript
/**
 * Render the Phase 1 operator shell.
 *
 * What: Shows Login and Dashboard skeleton regions plus backend health
 * status.
 * Why: Later UI phases need a stable app root while domain surfaces remain
 * out of scope.
 *
 * @returns The React app shell for Phase 1.
 */
export function App(): JSX.Element {
}
```

Pseudo code:

```text
create Vite React TypeScript scaffold
configure Vite dev proxy so frontend calls `/health` without a new env var
call fetchHealth from App on mount
render login region, dashboard shell region, and health status
do not render customers, payments, calls, review, exports, or admin flows
```

#### Compose And Local Environment Skeleton

Files:

- [compose.yml](../../compose.yml) (new).
- [.env.example](../../.env.example) (new).
- [backend/app/worker.py](../../backend/app/worker.py) (new).

Planned signatures and docstrings:

```python
def main() -> None:
    """Start the Phase 1 worker placeholder.

    What: Boots a no-op process that proves compose can start a worker
        container.
    Why: Later processing phases need a reserved worker service name, but
        Phase 1 must not enqueue or process reconciliation jobs.

    States / Side Effects:
        Writes a startup log line and then exits successfully.
    """
```

Pseudo code:

```text
declare postgres, redis, ollama, backend, frontend, and worker services
wire backend and worker env from .env.example values
set RECONAI_PROCESSING_ENABLED=false locally for Phase 1
mount named postgres, redis, ollama, and storage volumes
make worker run backend.app.worker main placeholder
document no domain queues or Celery tasks are created in this phase
```

### Refactor

- Move duplicated test environment setup into narrow backend and frontend
  test helpers only after Red tests pass.
- Keep env names aligned with [CONFIG.md](CONFIG.md#environment-variables)
  and feature flags aligned with [CONFIG.md](CONFIG.md#feature-flags).
- Keep package layout shallow: `backend/app/core` for foundation code,
  `backend/app/api` for future routers, `backend/app/features` for future
  domain modules, and `frontend/src/api` for the health client.
- Remove any placeholder implementation that adds reconciliation, auth,
  persistence, or tenant switching behavior beyond Phase 1 stubs.

## Setup and Testing in Local Dev

Settings and configuration:

- Copy [.env.example](../../.env.example) to `.env`.
- Set `DATABASE_URL` to the compose PostgreSQL URL.
- Set `REDIS_URL` to the compose Redis URL.
- Set `OLLAMA_BASE_URL` to the compose Ollama URL.
- Set `STORAGE_ROOT` to the compose storage volume path.
- Set `RECONAI_PROCESSING_ENABLED=false` for Phase 1.
- Set `RECONAI_NOTIFICATIONS_ENABLED=false`.
- Set `RECONAI_EXPORTS_ENABLED=false`; exports are not implemented yet.
- Set `WORKER_CONCURRENCY=1`.
- Install uv on the developer machine before backend setup.
- Treat `backend/.venv` as a local generated directory; do not commit it.
- Treat `backend/pyproject.toml` and `backend/uv.lock` as the reproducible
  backend environment contract.

Local run commands:

Backend local setup and tests:

```bash
cd backend
uv venv
uv sync
uv run python -m pytest tests/test_health.py tests/test_config.py \
  tests/test_context.py tests/test_compose_contract.py \
  tests/test_project_structure.py
uv run fastapi dev
```

Compose smoke run:

```bash
docker compose up --build
```

Frontend local test run:

```bash
cd frontend
npm test -- --run
```

Multi-tenant coverage:

- Addressed with fixture-level tenant identifiers in
  `test_context_stubs_keep_tenant_values_distinct`.
- Durable tenant seed data is N/A because Phase 1 has no database schema and
  no tenant-scoped runtime path.

Specific local test cases and expected outcomes:

| Test | Expected outcome |
| --- | --- |
| `test_health_endpoint_returns_ok` | `/health` returns 200 and the Phase 1 payload. |
| `test_settings_require_database_and_redis_urls` | Missing URLs fail validation with named errors. |
| `test_context_stubs_keep_tenant_values_distinct` | Two request contexts retain separate tenant values. |
| `test_compose_declares_foundation_services` | Compose contains required foundation services and volumes. |
| `test_backend_uses_uv_project_structure` | uv project files exist and `backend/.venv/` is ignored. |
| `test_frontend_app_renders_shell` | Login, Dashboard shell, and health surface render only. |
| `test_frontend_health_client_handles_ok_response` | Health client parses a 200 backend response. |

## Rollout Plan and Testing in QA and Staging

QA configuration:

- `RECONAI_PROCESSING_ENABLED=false`.
- `RECONAI_NOTIFICATIONS_ENABLED=false`.
- `RECONAI_EXPORTS_ENABLED=false`.
- Required URLs point to QA-managed PostgreSQL, Redis, Ollama, and storage
  resources or their QA compose equivalents.

Staging configuration:

- `RECONAI_PROCESSING_ENABLED=false` for Phase 1 smoke tests.
- `RECONAI_NOTIFICATIONS_ENABLED=false`.
- `RECONAI_EXPORTS_ENABLED=false`.
- `WORKER_CONCURRENCY=1`.

QA and staging test cases:

| Test | Expected outcome |
| --- | --- |
| Backend uv sync smoke | `cd backend && uv sync --frozen` succeeds without committing `.venv`. |
| Backend health smoke | `GET /health` returns 200 and service metadata. |
| Frontend shell smoke | The shell loads and shows backend health status. |
| Compose/service startup | PostgreSQL, Redis, Ollama, backend, frontend, and worker containers start. |
| Two-tenant fixture check | Tenant A and Tenant B context fixture values remain distinct. |

Data setup and migration steps:

- N/A for schema migrations; Phase 1 creates no database tables.
- N/A for durable seed data; fixture-level tenant values are enough for the
  planned tenant coverage.

## Rollout to Production

Ordered steps:

1. Build backend, frontend, and worker images from the Phase 1 scaffold;
   backend images install from `backend/pyproject.toml` and `backend/uv.lock`
   with uv rather than copying a local `backend/.venv`.
2. Provision environment values for `DATABASE_URL`, `REDIS_URL`,
   `OLLAMA_BASE_URL`, `STORAGE_ROOT`, and `WORKER_CONCURRENCY`.
3. Set `RECONAI_PROCESSING_ENABLED=false`,
   `RECONAI_NOTIFICATIONS_ENABLED=false`, and
   `RECONAI_EXPORTS_ENABLED=false`.
4. Start services with Docker Compose.
5. Verify `GET /health` from inside the network and through the public ingress
   if ingress is configured.
6. Open the frontend shell and verify it reports backend health.
7. Confirm worker placeholder starts, writes its startup log, exits with code
   0, and does not process jobs in Phase 1.

Expected outcomes:

- Backend health is reachable.
- Frontend shell renders.
- State-bearing services start with named volumes.
- No domain job, reconciliation action, audit write, export, notification, or
  tenant data mutation occurs.

Data setup and migration steps:

- N/A for migrations; no schema ships in Phase 1.
- N/A for tenant data rollback; Phase 1 writes no tenant-scoped data.

## SaaS Pre-Flight Disposition

| # | Item | Disposition | Evidence / Steps |
| --- | --- | --- | --- |
| 1 | Local dev multi-tenant coverage | Addressed | [Local dev](#setup-and-testing-in-local-dev) uses two distinct tenant context fixtures. |
| 2 | Tenant-aware test cases | Addressed | [Local dev](#setup-and-testing-in-local-dev) and [QA/staging](#rollout-plan-and-testing-in-qa-and-staging) run the two-tenant context check. |
| 3 | Per-environment feature flag state | Addressed | [Local](#setup-and-testing-in-local-dev), [QA/staging](#rollout-plan-and-testing-in-qa-and-staging), and [production](#rollout-to-production) set processing, notifications, and exports off. |
| 4 | Per-tenant canary rollout in production | N/A | Phase 1 exposes only a global health endpoint and shell; no tenant-facing behavior can be canaried. |
| 5 | Observability verification | N/A | Phase 1 has no metrics, traces, or tenant runtime path; production still verifies health responses and startup logs in [Rollout to Production](#rollout-to-production). |
| 6 | Audit log verification | N/A | Phase 1 has no audit-relevant mutation and no audit table. |
| 7 | Rate limit / quota verification | N/A | Phase 1 has only health and static shell behavior; rate limits land with protected APIs. |
| 8 | Webhook delivery verification | N/A | Base delivery webhooks are deferred and Phase 1 emits none. |
| 9 | Rollback addresses in-flight tenant data | N/A | Phase 1 creates no tenant data, migrations, queues, or domain writes. |
| 10 | Kill switch drill without redeploy | N/A | Phase 1 has no processing runtime to kill; the flag is pinned off in [Rollout to Production](#rollout-to-production) until worker behavior ships. |

## Summary of Changes

- [.gitignore](../../.gitignore) (new):
  Ignores `backend/.venv/` so the local uv environment stays untracked.
- [backend/pyproject.toml](../../backend/pyproject.toml) (new):
  Declares backend package metadata, dependencies, dev dependency group, and
  `[tool.fastapi]` entrypoint for P1, P2, and P5.
- [backend/uv.lock](../../backend/uv.lock) (new):
  Locks the backend uv project environment for reproducible setup.
- [backend/app/__init__.py](../../backend/app/__init__.py) (new):
  Marks the backend app package for P1 and P5.
- [backend/app/main.py](../../backend/app/main.py) (new):
  Adds the app factory, module-level app, health endpoint, and local dev
  entrypoint for P5 and P10.
- [backend/app/api/__init__.py](../../backend/app/api/__init__.py) (new):
  Reserves the future API router package for FastAPI larger-app structure.
- [backend/app/core/__init__.py](../../backend/app/core/__init__.py) (new):
  Marks the backend foundation package for P1 and P5.
- [backend/app/core/config.py](../../backend/app/core/config.py) (new):
  Adds typed settings loading for P2, P5, and P8.
- [backend/app/core/context.py](../../backend/app/core/context.py) (new):
  Adds ambient context and port stubs for P9.
- [backend/app/features/__init__.py](../../backend/app/features/__init__.py)
  (new): Reserves the future domain package while keeping behavior empty for
  P8.
- [backend/app/worker.py](../../backend/app/worker.py) (new):
  Adds the no-op worker placeholder for P7.
- [backend/tests/test_health.py](../../backend/tests/test_health.py) (new):
  Red test for the backend health endpoint required by P2 and P10.
- [backend/tests/test_config.py](../../backend/tests/test_config.py) (new):
  Red test for required settings validation required by P2.
- [backend/tests/test_context.py](../../backend/tests/test_context.py) (new):
  Tenant fixture coverage for P9 and SaaS pre-flight items 1-2.
- [backend/tests/test_compose_contract.py](../../backend/tests/test_compose_contract.py)
  (new): Practical compose validation for P4 and P7.
- [backend/tests/test_project_structure.py](../../backend/tests/test_project_structure.py)
  (new): Red test for uv project metadata, lockfile, and `.venv` ignore
  rules.
- [frontend/package.json](../../frontend/package.json) (new):
  Declares frontend tooling for P1, P3, and P6.
- [frontend/index.html](../../frontend/index.html) (new):
  Provides the Vite HTML entrypoint for P6.
- [frontend/vite.config.ts](../../frontend/vite.config.ts) (new):
  Adds the Vite React test/dev configuration for P3 and P6.
- [frontend/src/main.tsx](../../frontend/src/main.tsx) (new):
  Mounts the React app shell for P6.
- [frontend/src/App.tsx](../../frontend/src/App.tsx) (new):
  Adds the Login/Dashboard shell and health status surface for P6 and P10.
- [frontend/src/api/health.ts](../../frontend/src/api/health.ts) (new):
  Adds the health client for P3 and P6.
- [frontend/src/App.test.tsx](../../frontend/src/App.test.tsx) (new):
  Red test for the frontend shell required by P3 and P6.
- [frontend/src/api/health.test.ts](../../frontend/src/api/health.test.ts)
  (new): Red test for the frontend health client required by P3.
- [compose.yml](../../compose.yml) (new):
  Adds foundation services and placeholders for P7.
- [.env.example](../../.env.example) (new):
  Normalizes local environment names for P8.

## Code Generation Instructions

See `planning-conventions` ->
[Code Generation Instructions][codegen] -- lint, types, docstrings, commits,
and change-summary rules apply unchanged.

## Grounding Audit Result

- Verified `docs/customer_payment_reconciliation_agent/PLAN.md` exists and
  contains Phase 1.
- Verified upstream planning references exist in the same docs directory:
  [SPEC.md](SPEC.md), [ARCH.md](ARCH.md), [API.md](API.md),
  [DEFINITIONS.md](DEFINITIONS.md), [CONFIG.md](CONFIG.md),
  [TESTING.md](TESTING.md), and [UI_UX.md](UI_UX.md).
- Verified the app folders currently contain only
  [backend/.gitkeep](../../backend/.gitkeep) and
  [frontend/.gitkeep](../../frontend/.gitkeep), so planned runtime files are
  new files.
- No Alembic, package manifest, uv lockfile, repo ignore file, compose file,
  or runtime entrypoint currently exists; this is recorded as an assumption in
  the coverage ledger.

## Questions for Clarification

None for Phase 1. Open product gates in [PLAN.md](PLAN.md#clarification-gates)
do not block this scaffold-only phase because it does not implement
extraction, tenant administration, notifications, CSV import, retention, or
review authorization behavior.

<details>
<summary>Coverage Ledger</summary>

| ID | Category | Source | Pushed to (owner file) | Status |
| --- | --- | --- | --- | --- |
| L1 | inherited | [PLAN.md Phase 1 summary][plan-p1] | - | resolved |
| L2 | inherited | [PLAN.md Phase 1 Red][plan-p1] | - | resolved |
| L3 | inherited | [PLAN.md Phase 1 Green][plan-p1] | - | resolved |
| L4 | inherited | [PLAN.md Phase 1 Refactor][plan-p1] | - | resolved |
| L5 | inherited | [DEFINITIONS.md Ambient Context Types](DEFINITIONS.md#ambient-context-types) | - | resolved |
| L6 | inherited | [PLAN.md Phase 1 Mapping][plan-p1] | - | resolved |
| L7 | inherited | [UI_UX.md Screen Inventory](UI_UX.md#screen-inventory) | - | resolved |
| L8 | inherited | [CONFIG.md Feature Flags](CONFIG.md#feature-flags) | - | resolved |
| L9 | inherited | Phase 1 subset of [CONFIG.md Environment Variables](CONFIG.md#environment-variables) | - | resolved |
| L10 | inherited | [TESTING.md Tooling](TESTING.md#tooling) | - | resolved |
| L11 | inherited | [ARCH.md System Context](ARCH.md#4-system-context) | - | resolved |
| L12 | phase-local | Phase 1 Red test names in this document | - | phase-local |
| L13 | phase-local | Phase 1 sizing estimate in this document | - | phase-local |
| L14 | phase-local | SaaS pre-flight dispositions in this document | - | phase-local |
| L15 | phase-local | uv/FastAPI research basis in this document | - | phase-local |
| L16 | phase-local | backend uv project structure and `.venv` ignore rules | - | phase-local |
| L17 | assumption | [backend/.gitkeep](../../backend/.gitkeep) and [frontend/.gitkeep](../../frontend/.gitkeep) are the only app files | - | verified in code |
| L18 | assumption | User requested `PHASE-1.md` filename | - | verified in prompt |
| L19 | assumption | No durable tenant seed is required because Phase 1 has no schema or tenant runtime | - | verified in source docs |

</details>

[plan-p1]: PLAN.md#phase-1-300-450-loc-production--180-280-tests-archetype-contract-freeze--stubs-only-project-foundation
[codegen]: ../../.agents/skills/planning-conventions/SKILL.md#code-generation-instructions
