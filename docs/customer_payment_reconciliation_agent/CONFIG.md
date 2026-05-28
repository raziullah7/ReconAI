# CONFIG.md

> Status: This document separates current required settings from future target
> settings. A setting listed as deferred should not be required by the app yet.

## Current Required Configuration

### DATABASE_URL

Type: environment variable.

Purpose: PostgreSQL connection string for the local backend.

Current default for local development:

```bash
DATABASE_URL=postgresql+psycopg://reconai:reconai@localhost:5432/reconai
```

Validation: must use a PostgreSQL SQLAlchemy scheme. Milestone 1 database
phases use psycopg 3, so local SQLAlchemy/Alembic URLs use
`postgresql+psycopg://`.

Runtime: restart the backend after changing it.

Tenant override: not allowed.

## Current Local Commands

Start the database from the repo root:

```bash
docker compose up -d postgres
```

Apply migrations and start the backend from `backend/`:

```bash
uv sync
DATABASE_URL=postgresql+psycopg://reconai:reconai@localhost:5432/reconai uv run alembic upgrade head
DATABASE_URL=postgresql+psycopg://reconai:reconai@localhost:5432/reconai uv run fastapi dev --host 127.0.0.1 --port 8000
```

## Planned Milestone 1 Configuration

### EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD

Type: environment variable.

Purpose: numeric threshold for routing low-confidence agreement extractions to
`NEEDS_REVIEW` during Base API decision-making.

Default for Milestone 1: `0.80`. Values below `0.80` route the case to
`NEEDS_REVIEW`; values equal to or above `0.80` may be automatically
decided when the rest of the extraction and payment evidence is valid.

Current status: not required by the Phase 1 foundation app. Milestone 1
introduces this setting during validation and decision implementation.

Runtime: restart the backend after changing it once the Base API phase
introduces this setting.

Tenant override: deferred until tenant context exists.

## Deferred Configuration

These settings are part of the target product, but they should not be required
in the current foundation phase.

| Setting | Introduced In | Reason It Is Deferred |
| --- | --- | --- |
| `REDIS_URL` | Redis and queue foundation phase | No queue or worker behavior exists yet. |
| `OLLAMA_BASE_URL` | Local AI boundary phase | No local LLM adapter exists yet. |
| `RECONAI_LLM_MODEL` | Local AI boundary phase | Model choice is still gated. |
| `TRANSCRIPTION_BACKEND` | Local AI boundary phase | Transcription adapter is not implemented yet. |
| `STORAGE_ROOT` | Call intake or storage phase | No recording/export storage path exists yet. |
| `WORKER_CONCURRENCY` | Worker runtime phase | No worker process exists yet. |
| `RECONAI_PROCESSING_ENABLED` | Worker runtime phase | There is no processing pipeline yet. |
| `RECONAI_NOTIFICATIONS_ENABLED` | Notification phase, if kept in scope | Notifications are not in the early build. |
| `RECONAI_EXPORTS_ENABLED` | Dashboard/export phase | Exports are not implemented yet. |
| `EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD` | Base API validation/decision phase | Default is `0.80`; it is not required by Phase 1. |

## Open Questions

- Revisit the `0.80` extraction confidence threshold after real local LLM
  fixture data exists.
- Confirm the local LLM model before adding Ollama or worker sizing docs.
- Confirm CSV import columns before payment import is planned.
