# ReconAI: Payment Reconciliation Application

**In development.** ReconAI checks payment agreements against payment evidence, then saves the result and the reason for it. The FastAPI backend is on `main`. Frontend work is on separate branches, linked below.

## Implemented features

- Create, list, filter, and retrieve reconciliation cases through versioned API endpoints.
- Validate agreement and payment input with Pydantic, including currency, confidence, and evidence requirements.
- Apply deterministic rules for reconciled, underpaid, overpaid, partial-payment, missing-payment, and review-required outcomes.
- Store input snapshots, decisions, and timestamps in PostgreSQL using SQLAlchemy and Alembic migrations.
- Return the amount difference, decision reason, confidence, and review flag with each result.

Amounts use integer minor units. The current API accepts structured extraction data and an optional payment snapshot; automatic AI extraction from source text is planned.

## Architecture and workflow

```text
Structured agreement + optional payment
                  |
             FastAPI router
                  |
        Pydantic input validation
                  |
      Service + deterministic rules
                  |
       SQLAlchemy repository layer
                  |
              PostgreSQL
```

A request to `POST /v1/reconciliation-cases` is validated, evaluated, and persisted. `GET /v1/reconciliation-cases` returns summaries with optional `status`, `limit`, and `offset` parameters; `GET /v1/reconciliation-cases/{case_id}` returns the stored detail. The backend owns the final reconciliation decision.

Explore the [API routes](backend/app/routers/reconciliation_cases.py), [decision rules](backend/app/domain/reconciliation/decisions.py), and [architecture documentation](docs/customer_payment_reconciliation_agent/ARCH.md).

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

This synthetic example represents a USD 100 agreement and matching payment. See the [backend guide](backend/README.md) for the existing setup and command reference.

## Existing checks

Run from `backend/`:

```bash
uv run python -m pytest
uv run mypy app
uv run ruff check .
```

The [test suite](backend/tests) includes API, service, repository, validation, and decision-rule tests, alongside health and configuration checks. These are the repository's check commands; this overview does not claim a fresh test run.

## Current status

| Area | Status |
| --- | --- |
| Backend on `main` | Structured-input reconciliation API, persistence, and backend tests are implemented. |
| Frontend integration | [PR #9](https://github.com/raziullah7/ReconAI/pull/9), from [`m2-base-frontend`](https://github.com/raziullah7/ReconAI/tree/m2-base-frontend), contains the React/TypeScript frontend with case-list and detail work; it is separate from `main`. |
| Submission and result UI | Additional work is available on [`m2-5-submit-result`](https://github.com/raziullah7/ReconAI/tree/m2-5-submit-result). |
| AI extraction | Planned. The current API accepts supplied structured data; it does not call a model to extract an agreement. |

To explore the frontend, use the [frontend branch's setup guide](https://github.com/raziullah7/ReconAI/blob/m2-base-frontend/frontend/README.md). The [product documentation index](docs/customer_payment_reconciliation_agent/README.md) and [milestone plan](docs/customer_payment_reconciliation_agent/PLAN.md) describe the broader roadmap; planned features are not all implemented.
