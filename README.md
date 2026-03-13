# Guadalajara Wine Finder

Batch-first web app for two users to discover affordable wines in Guadalajara, collect tasting feedback, and surface explainable recommendations.

## Stack

- Backend: FastAPI
- Database: PostgreSQL-compatible schema (SQLite default for local dev)
- Scheduler: Python CLI entrypoint (cron/GitHub Actions compatible)
- Frontend: Static HTML/JS served by FastAPI
- LLM: Provider-agnostic adapter with strict JSON schema validation

## Quick start

1. Create a virtual environment and install dependencies:
   - `pip install -e ".[dev]"`
2. Start API:
   - `uvicorn app.main:app --reload`
3. Trigger a pipeline run:
   - `python scripts/run_pipeline.py --mode daily`
4. Run tests:
   - `pytest -q`

## Defaults

- Database URL: `sqlite:///./data/app.db`
- Users:
  - `A` / password from `USER_A_PASSWORD` (default `changeme-a`)
  - `B` / password from `USER_B_PASSWORD` (default `changeme-b`)

## Important project policies

- Run artifacts are written to `artifacts/<run_id>/...`
- Raw page snapshots are written to `artifacts/raw_pages/<yyyy-mm>/<hash>.html`
- Logs, raw pages, and generated artifacts are ignored by git
- Prompt templates are versioned in `prompts/`
- JSON contracts are versioned in `schemas/`

## Frontend companion docs

- `docs/frontend-information-architecture.md`
- `docs/frontend-component-spec.md`
- `docs/frontend-api-contract.md`
- `docs/frontend-design-tokens.md`
- `docs/frontend-acceptance-checklists.md`
