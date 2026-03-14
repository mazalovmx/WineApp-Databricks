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
5. Run in Docker:
   - `docker compose up -d --build`

## Defaults

- Database URL: `sqlite:///./data/app.db`
- Users:
  - `A` (`Alexander`) / password from `USER_A_PASSWORD` (default `changeme-a`)
  - `B` (`Elena`) / password from `USER_B_PASSWORD` (default `changeme-b`)
- User preferences are isolated by user id (`A` and `B`) and persisted separately.

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
- `docs/plans/frontend-user-journeys-25.md`

## Testing docs

- `docs/testing.md`
- `docs/plans/testing-issue-hunt-plan.md`

## Demo data docs

- `docs/demo-data.md`

## Repository hygiene and docs-as-code

- `docs/plans/repository-hygiene-plan.md`
- `docs/policies/docs-as-code.md`
- `docs/one_time/README.md`

## Deployment and provider docs

- `docs/deployment.md`
- `docs/llm-agnostic.md`

## Scheduled pipeline execution

- GitHub Actions schedule workflow: `.github/workflows/pipeline_schedule.yml`
- Default UTC schedule:
  - daily: `0 6 * * *`
  - weekly: `0 7 * * 1`
- Manual launch with mode:
  - Actions → `Pipeline Schedule` → `Run workflow` → select `daily|weekly|manual`

Quality/doc enforcement scripts:

- `python3 scripts/repo_hygiene_check.py`
- `python3 scripts/docs_guard.py --base-ref HEAD~1`
- `python3 scripts/run_quality_pipeline.py --base-ref HEAD~1`
- `python3 scripts/run_ui_issue_hunt.py`
