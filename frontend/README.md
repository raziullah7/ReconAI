# ReconAI Frontend

Local Vite frontend for ReconAI.

## Setup

```bash
npm install
cp .env.example .env
```

## Run With Backend

Terminal 1 from the repo root:

```bash
docker compose up -d postgres
cd backend
uv run alembic upgrade head
uv run fastapi dev --host 127.0.0.1 --port 8000
```

Terminal 2 from `frontend/`:

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```

## Check

```bash
npm run build
npm run lint
```
