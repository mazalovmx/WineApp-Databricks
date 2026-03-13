# Deployment Guide (Auto + Any Server)

## Goal

Ship the app automatically to a Linux server with Docker/Compose.

## Included assets

- `Dockerfile`
- `.dockerignore`
- `docker-compose.yml`
- `.github/workflows/deploy_server.yml`

## Server prerequisites

1. Docker Engine + Docker Compose plugin installed.
2. SSH access with key-based auth.
3. Outbound network access to fetch repository.

## GitHub secrets for auto-deploy

- `DEPLOY_HOST`: server host/IP
- `DEPLOY_USER`: SSH user
- `DEPLOY_SSH_KEY`: private key for deployment user
- `DEPLOY_REPO_URL`: read-only Git URL (SSH/HTTPS)

## How auto-deploy works

1. Workflow triggers on push to `main` or manual dispatch.
2. CI validates deployment files and builds image.
3. If secrets exist, CI connects to server over SSH.
4. Server pulls latest `main` and runs:
   - `docker compose up -d --build`

## Runtime configuration

Use environment variables from `docker-compose.yml`:

- app/auth: `APP_SECRET`, `USER_A_PASSWORD`, `USER_B_PASSWORD`
- data: `DATABASE_URL`
- LLM adapter: `LLM_PROVIDER`, `LLM_*_URL`, `LLM_HEADERS_JSON`, `LLM_TIMEOUT_SECONDS`

## Health checks after deploy

1. `curl http://<server>:8000/health`
2. Open `/` in browser.
3. Login as A/B and run smoke checks:
   - `python3 scripts/run_ui_issue_hunt.py`
