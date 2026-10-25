# Architecture Archaeologist

> Dig through a codebase's architecture — ingest, explore, ask.

Ingest repositories and the engine maps their architecture, answers questions about structure and dependencies, and produces archaeology reports on how the system actually works.

## Features

- Repo ingestion and dependency mapping
- Architecture explorer
- Natural-language Q&A over the codebase
- Archaeology reports per repository

## Architecture

| Layer | Stack | Path |
|---|---|---|
| Frontend | Astro (file-based routing) | `frontend/` |
| Backend | FastAPI + SQLAlchemy + Pydantic | `backend/` |
| Tests | pytest | `backend/tests/` |

Frontend routes: `ingest, explorer, ask, report`.

## Quick start

Backend (from `backend/`):

```bash
pip install -r requirements.txt
cp .env.example .env        # optional — works with no keys
python3 -m uvicorn app.main:app --port 8001
```

Frontend (from `frontend/`):

```bash
npm install
npm run dev
```

Tests: `python3 -m pytest backend/tests/ -v`

## Deployment

The frontend builds to a static bundle and deploys to GitHub Pages on every
push to `main` (`.github/workflows/deploy.yml`):

**https://adineo-cmd2.github.io/architecture-archaeologist/**

## Project structure

```
backend/
  app/          FastAPI application
  tests/        pytest suite
frontend/
  src/pages/    Astro routes
```
