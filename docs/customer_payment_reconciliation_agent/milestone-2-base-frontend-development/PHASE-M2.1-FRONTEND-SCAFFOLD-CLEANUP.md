# PHASE-M2.1-FRONTEND-SCAFFOLD-CLEANUP.md

## Executive Summary

This phase turns the user-created Vite starter scaffold into a minimal ReconAI
frontend shell. It removes starter UI, starter assets, template README content,
and irrelevant default template code so future phases start from a small app
that is easy to understand. It preserves the default frontend initialization
tooling and dependencies, including the React Compiler setup.

Expected outcome: `frontend/` builds and lints as a ReconAI shell, but it does
not call the backend yet.

Assumptions:

- The existing uncommitted Vite scaffold is the starting point for Milestone 2.
- This phase is frontend-only and does not modify backend CORS, APIs, database,
  Docker, Redis, Ollama, workers, auth, or tenant behavior.
- Default Vite/React tooling and dependency setup stays in place unless a file
  is only a starter UI asset.
- The shell is intentionally static until M2.2 and M2.3 introduce connectivity
  and data behavior.

P_bottom_up: about 120 production LOC changed, mostly removing starter UI and
rewriting the shell styles and README.
T_bottom_up: 0 test LOC because verification uses build and lint only.

## Execution Plan

### Red

- `frontend_build_current_starter_references_are_removed`
  - Summary: Inspect the scaffold and confirm starter references still exist
    before cleanup.
  - Mocks: None.
  - Assertions: `src/App.tsx`, `src/App.css`, `src/index.css`,
    `frontend/README.md`, and `index.html` contain Vite/React starter content
    or starter naming before Green removes it.

- `frontend_build_and_lint_after_cleanup`
  - Summary: The cleaned shell must still compile and lint.
  - Mocks: None.
  - Assertions: `npm run build` and `npm run lint` pass from `frontend/`.

### Green

- Replace `frontend/src/App.tsx` with a small static ReconAI app shell.
- Replace starter styles in `frontend/src/App.css` and
  `frontend/src/index.css` with restrained app-shell styling that does not use
  Vite/React branding, oversized landing-page hero treatment, or instructional
  template copy.
- Update `frontend/index.html` title to `ReconAI`.
- Replace `frontend/README.md` with local setup and run commands for the
  frontend only.
- Remove unused starter assets from `frontend/src/assets/` and
  `frontend/public/`; keep the default favicon unless a later phase introduces
  a project-specific icon.
- Preserve `frontend/vite.config.ts`, `frontend/package.json`, and
  `frontend/package-lock.json` dependency/tooling setup except for harmless app
  metadata such as the package name.

Pseudo code for the shell:

```text
render app root
    render top-level app frame labelled ReconAI
    render a compact empty workspace shell
    do not describe future workflow instructions in visible UI copy
    do not fetch data
    do not define mock case data
```

### Refactor

- Keep the shell in `App.tsx` until M2.3 has enough behavior to justify smaller
  components.
- Keep CSS global and local files small; do not introduce a design system or
  component library in this phase.

## Setup and Testing in Local Dev

Settings and configuration: none for this phase.

Environment variables: none for this phase.

Local commands:

```bash
cd frontend
npm install
npm run build
npm run lint
rg -n "React logo|Count is|Get started|vite.svg|react.svg|HMR|vite.dev|react.dev|hero.png|icons.svg" . -g '!node_modules' -g '!package-lock.json'
```

The final `rg` command should return no starter UI references, except package
names that are legitimate React/Vite tooling references.

## What You Can Run After This Phase

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Expected outcome: a local ReconAI shell opens without backend connectivity or
mock data.

## Rollout Notes

- Local: run the commands above.
- QA/Staging/Production: N/A because the frontend is not deployed in this
  phase.
- Rollback: revert this phase to return to the starter scaffold. No backend or
  database state is affected.

## Summary of Changes

- Change frontend shell files and README.
- Delete unused starter assets.
- Preserve default frontend dependencies and compiler tooling.

## Out of Scope

- Backend CORS and API base URL config.
- API client functions, fetch calls, seed data, and mock-only screens.
- Frontend unit, component, API-client, and browser tests.
- Frontend Docker, Redis, Ollama, workers, auth, tenants, dashboards, exports,
  and payment-ledger behavior.

## Coverage Ledger

| Item | Category | Source | Notes |
| --- | --- | --- | --- |
| Frontend starts in Milestone 2 as local Vite only | inherited | [../PLAN.md](../PLAN.md#milestone-2-base-frontend-development) | Limits work to frontend scaffold cleanup. |
| No API calls in M2.1 | phase-local | This phase summary | Keeps connectivity in M2.2. |
| Build and lint verification | inherited | [../TESTING.md](../TESTING.md#milestone-2-base-frontend-verification) | Scaffold cleanup has no frontend tests. |
| Preserve default frontend tooling | phase-local | This phase assumptions | React Compiler and default dependencies stay. |
| Existing scaffold is user-created | assumption | Reality check against `frontend/` | Implementation must not discard unrelated user changes. |
