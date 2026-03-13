# Guadalajara Wine Finder

A small personal web app for two users to discover cheap, tasty wines in Guadalajara, Jalisco from supermarkets and specialty wine shops.

## Features

- **Recommended Buys**: Daily/weekly new wines likely to match each user's taste at good prices
- **Cheapest Favorites**: Wines already liked, showing where they're currently cheapest
- **Taste Profiles**: Separate ratings (1–5) and comments for each user
- **Bilingual UI**: English and Russian support

## Architecture

- **Frontend**: Next.js + React (RU/EN toggle)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Pipeline**: Scheduled batch (cron or GitHub Actions)
- **Storage**: Local `./data/` for MVP; S3-compatible for production

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Setup

```bash
# From project root
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r backend/requirements.txt
pip install -r pipeline/requirements.txt
cp backend/.env.example backend/.env  # Configure your environment
```

### Database

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/winefinder"
cd backend && alembic upgrade head && cd ..
python scripts/seed_db.py  # Create users A, B and seed stores
```

### Backend API

```bash
# From project root, with venv activated
PYTHONPATH=. uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

### Pipeline (scheduled run)

```bash
# From project root
PYTHONPATH=. python -m pipeline.runner daily
# Or weekly: PYTHONPATH=. python -m pipeline.runner weekly
```

### Frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

### Default Auth (MVP)

- User A: password `user_a` (or `USER_A_PASSWORD` env)
- User B: password `user_b` (or `USER_B_PASSWORD` env)

### Environment Variables

See `backend/.env.example` for configuration. Key: `DATABASE_URL`, `SECRET_KEY`, optional `LLM_API_KEY`.

## Project Structure

```
├── backend/          # FastAPI application (src/main.py)
├── frontend/         # Next.js web UI
├── pipeline/         # Batch pipeline (runner + steps)
├── prompts/          # LLM prompt templates
├── data/             # Seed sources, raw pages (not committed)
└── scripts/          # Seed script
```

## License

Personal use.
