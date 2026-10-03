# Local development and checks

[Project overview](../README.md)

## Setup and usage

Requirements: Python **3.14+**, [uv](https://docs.astral.sh/uv/), and Docker with Compose. PostgreSQL runs in Docker; the backend runs in a local Python environment.

From a checkout of `main`:

```bash
docker compose up -d postgres
cd backend
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run fastapi dev --host 127.0.0.1 --port 8000
```

On PowerShell, `Copy-Item .env.example .env` can replace the copy command. Review `DATABASE_URL` and `EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD` in your local `.env`; the example targets the repository's local PostgreSQL service.

Open [interactive API documentation](http://127.0.0.1:8000/docs), or check the running API:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1/reconciliation-cases
```

Use the interactive documentation to submit a case with a request such as:

```json
{
  "external_reference": "demo-001",
  "extraction": {
    "schema_version": "agreement_extraction.v1",
    "agreed_amount_minor": 10000,
    "currency": "USD",
    "payment_type": "FULL_PAYMENT",
    "is_final_amount": true,
    "confidence": 0.95,
    "needs_human_review": false
  },
  "actual_payment": {
    "paid_amount_minor": 10000,
    "currency": "USD"
  }
}
```

This synthetic example represents a USD 100 agreement and matching payment. See the [backend guide](../backend/README.md) for the existing setup and command reference.

## Existing checks

Run from `backend/`:

```bash
uv run python -m pytest
uv run mypy app
uv run ruff check .
```

The [test suite](../backend/tests) includes API, service, repository, validation, and decision-rule tests, alongside health and configuration checks. These are the repository's check commands; this overview does not claim a fresh test run.


