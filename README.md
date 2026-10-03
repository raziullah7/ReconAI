# ReconAI

**In development.** A Python/FastAPI application that compares payment agreements with payment evidence and stores the decision in PostgreSQL.

## Implemented

- Create, list, filter, and retrieve reconciliation cases.
- Validate structured input with Pydantic.
- Apply deterministic reconciliation and review rules.
- Persist input snapshots, decisions, reasons, and timestamps through SQLAlchemy and Alembic.
- Represent amounts in integer minor units.

The backend is on `main`. React/TypeScript frontend integration is tracked in [PR #9](https://github.com/raziullah7/ReconAI/pull/9); additional submission/result work is on [m2-5-submit-result](https://github.com/raziullah7/ReconAI/tree/m2-5-submit-result). These branches are separate from the default-branch implementation at this documentation update.

**AI extraction is planned.** The current API accepts supplied structured data; it does not extract agreements by calling a model.

## Run and inspect

Requires Python 3.14+, uv, and Docker Compose. Follow the [setup and API example](docs/SETUP.md), then open `http://127.0.0.1:8000/docs`.

From `backend/`, the configured checks are:

```bash
uv run python -m pytest
uv run mypy app
uv run ruff check .
```

These commands were not executed for this documentation update.

[API routes](backend/app/routers/reconciliation_cases.py) · [Decision rules](backend/app/domain/reconciliation/decisions.py) · [Architecture](docs/customer_payment_reconciliation_agent/ARCH.md)

