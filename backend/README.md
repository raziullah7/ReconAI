# Backend

Minimal FastAPI backend setup for the current phase.

## Setup

Create or refresh the local uv environment:

```bash
uv sync
```

The virtual environment lives at `.venv/` inside this folder and should stay
untracked.

## Run

Start Postgres from the repo root:

```bash
docker compose up -d postgres
```

Then start the backend from this folder:

```bash
DATABASE_URL=postgresql+psycopg://reconai:reconai@localhost:5432/reconai uv run fastapi dev --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Test

```bash
uv run python -m pytest
```

Optional checks:

```bash
uv run mypy app
uv run ruff check .
```
