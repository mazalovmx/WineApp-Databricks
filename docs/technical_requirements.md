# Technical Requirements Specification — Guadalajara Wine Finder

## 0) Purpose and Scope

Guadalajara Wine Finder is a small personal web app for two users (User A and User B) to:
1. Discover cheap, tasty wines in Guadalajara, Jalisco from supermarkets and specialty wine shops.
2. Track separate taste profiles (ratings 1–5 + comments) for each user.
3. Produce two outputs:
   - Daily/Weekly Recommended Buys.
   - Cheapest Favorites.

The system runs as a scheduled batch pipeline plus a small API for the UI.

## 1) High-Level Architecture

Components:
- Frontend (web UI with RU/EN toggle)
- Backend API (FastAPI)
- Scheduler / Worker (daily/weekly/manual batch runs)
- Relational database (PostgreSQL-compatible schema)
- Object storage for artifacts/raw snapshots (local artifacts in MVP)
- LLM provider adapter (provider-agnostic interface)

Key principle: batch-first architecture; UI reads prepared results.

## 2) Core Functional Requirements

- Exactly two users (A/B) with locale and taste profile.
- Guadalajara sources only: network supermarkets and specialty shops.
- Scheduled ingestion: discover pages, fetch pages, extract offers, dedupe/normalize.
- Review enrichment for discovered wines.
- Recommendation outputs:
  - Recommended Buys (new wines, prioritize 100–400 MXN, permit wow deals)
  - Cheapest Favorites (liked wines threshold >= 4)
  - Explainability text with reasons and uncertainty handling
- Tasting feedback: tried/rating/comment.
- Tried wines search/filter.
- RU/EN UI support.

## 3) Data Model (Relational)

Minimum canonical tables:
- users
- stores
- wines
- offers
- price_history
- raw_pages
- external_reviews
- review_aggregates
- user_ratings
- recommendation_runs
- recommendations
- interaction_events (optional MVP+)

Matching requirements:
- deterministic normalization and heuristic matching first
- optional LLM-assisted matching
- confidence tracked

## 4) LLM Integration (Provider-Agnostic)

Capabilities:
- search/browse
- strict JSON extraction
- summarization with uncertainty
- classification

Required adapter methods:
- `search(query)`
- `extract_offers(page_text, schema)`
- `summarize_reviews(texts)`
- `match_wine_entity(listed_name, candidates)`

All prompts are versioned in `prompts/` and validated with JSON schemas.

## 5) API Requirements

Minimal endpoints:
- `GET /health`
- `POST /auth/login`
- `GET /users/me`
- `GET /recommendations`
- `GET /favorites/cheapest`
- `GET /wines/tried`
- `POST /ratings`
- `POST /runs/trigger`

## 6) Scheduled Pipeline

Modes:
- daily
- weekly
- manual

Canonical steps:
1. source discovery
2. fetch pages
3. extract offers
4. normalize/dedupe
5. enrich reviews
6. score/rank
7. write outputs
8. write logs/artifacts

Failure handling:
- partial failures do not corrupt past results
- retries with backoff
- stale-source visibility

## 7) Scoring and Explainability

Hard filters:
- exclude sweet wines
- exclude non-grape wines
- Guadalajara-only sources

Inputs:
- price (dominant)
- discount bonus
- review score bonus
- descriptor-user match bonus
- wow deal bonus

Each recommendation includes concise reasons.

## 8) Frontend Requirements

Pages:
- Home (recommended buys, cheapest favorites, last refresh)
- Tried wines (search/filter/history)
- Add rating
- Settings (user selection, language toggle, schedule display/manual run)

## 9) Logging and Artifacts

- Structured logs per run.
- Artifacts in `artifacts/<run_id>/...`.
- Raw snapshots in hashed storage paths.
- No artifacts committed to git.

## 10) Non-Functional Requirements

- Batch completion target: <30–60 minutes at MVP scale.
- API response target: <1s normal queries.
- Idempotent runs.
- Versioned DB migrations (future increment).
- Cost controls for page and LLM usage.
- Secrets in environment variables.

## 11) Testing Requirements

- Unit tests: parsing/scoring/schema/matching helpers.
- Integration tests: pipeline and API.
- Contract tests: JSON schema contracts for extraction and reviews.

## 12) Deliverables / Definition of Done

MVP deliverables:
- scheduled run
- UI for recommendations, tried wines, ratings
- explainable recommendations
- raw + normalized storage

PR done:
- tests pass
- lint pass
- docs updated
- no artifacts committed
- schema updates for DB changes
