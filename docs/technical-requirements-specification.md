# Technical Requirements Specification — Guadalajara Wine Finder

## 0. Purpose and Scope

Guadalajara Wine Finder is a small personal web app for two users (User A and User B) to:

1. **Discover cheap, tasty wines** in Guadalajara, Jalisco from supermarkets and specialty wine shops.
2. **Track separate taste profiles** (ratings 1–5 + comments) for each user.
3. **Produce two main outputs:**
   - **Daily/Weekly "Recommended Buys"** — new wines likely to match each user's taste at good prices.
   - **"Cheapest Favorites"** — wines already liked, showing where they're currently cheapest, with total price.

The system runs primarily as a **scheduled batch pipeline** (daily or weekly) plus a small API for the UI.

---

## 1. High-Level Architecture (Simple and Robust)

### 1.1 Components

#### 1. Frontend (Web UI)

- Static web app (Next.js/React or plain HTML + minimal JS).
- Talks to backend via HTTPS JSON API.
- Supports RU/EN language toggle.

#### 2. Backend API (Application Server)

- Python (FastAPI) recommended for simplicity.
- Responsibilities:
  - Authentication for two users.
  - Serving recommendation outputs.
  - Accepting tasting feedback (rating + comment).
  - Serving search/filter queries over "tried wines".
  - Exposing operational status ("last run", "data freshness").

#### 3. Scheduler / Worker

- Runs the batch pipeline:
  - discover sources → fetch pages → extract structured data → dedupe/normalize → enrich with reviews → score and write outputs
- Could be:
  - A cron job on a VPS.
  - GitHub Actions schedule.
  - A serverless scheduled function.
  - A container on a cheap cloud instance.

#### 4. Database (Relational)

- PostgreSQL recommended.
- Stores canonical entities, offers, histories, user feedback, and prepared outputs.

#### 5. Object Storage (Optional but Recommended)

- S3-compatible bucket (or local filesystem in early dev).
- Stores raw page snapshots (HTML/text), extraction payloads, and run artifacts.

#### 6. LLM Provider with Web Search

- Must support:
  - Web search tool / browsing capability (or you implement your own search + scraping).
  - Structured extraction (JSON).
  - Summarization of external reviews.
- **Provider-agnostic adapter layer required.**

### 1.2 Key Design Principle

> **Batch-first architecture:** the system's intelligence happens in the scheduled run. The UI reads prepared results; runtime LLM calls in the UI should be optional and rare.

### 1.3 Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          GUADALAJARA WINE FINDER                           │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐     HTTPS/JSON     ┌──────────────────┐                  │
│  │   Frontend    │◄─────────────────►│   Backend API     │                  │
│  │  (Next.js /   │                   │   (FastAPI)       │                  │
│  │   React)      │                   │                   │                  │
│  │              │                   │  - Auth            │                  │
│  │  - RU/EN     │                   │  - Recommendations │                  │
│  │  - Ratings   │                   │  - Ratings CRUD    │                  │
│  │  - Search    │                   │  - Wine search     │                  │
│  └──────────────┘                   │  - Run status      │                  │
│                                      └────────┬─────────┘                  │
│                                               │                            │
│                                      ┌────────▼─────────┐                  │
│                                      │   PostgreSQL DB   │                  │
│                                      │                   │                  │
│  ┌──────────────┐                   │  - wines          │                  │
│  │  Scheduler /  │──────────────────►│  - offers         │                  │
│  │  Worker       │                   │  - ratings        │                  │
│  │  (cron/CI)    │                   │  - reviews        │                  │
│  │              │                   │  - recommendations│                  │
│  │  Batch        │                   └──────────────────┘                  │
│  │  Pipeline     │                                                         │
│  └──────┬───────┘                   ┌──────────────────┐                  │
│         │                            │  Object Storage   │                  │
│         │                            │  (S3 / local)     │                  │
│         └───────────────────────────►│                   │                  │
│                                      │  - raw pages      │                  │
│  ┌──────────────┐                   │  - artifacts      │                  │
│  │  LLM Provider │                   │  - logs           │                  │
│  │  (pluggable)  │                   └──────────────────┘                  │
│  │              │                                                         │
│  │  - Web search │                                                         │
│  │  - Extraction │                                                         │
│  │  - Summarize  │                                                         │
│  └──────────────┘                                                         │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Functional Requirements

### 2.1 Users and Profiles

- The system supports exactly **two user identities** (User A, User B).
- Each user has:
  - Language preference (EN/RU).
  - Taste profile derived from their ratings/history.
- The system must produce:
  - **User-specific recommendations.**
  - **"Joint" recommendations** (optional) for shared purchases.

### 2.2 Sources and Coverage

- **Geography:** Guadalajara, Jalisco only.
- **Source categories:**
  - "Network supermarkets"
  - "Specialty wine/alcohol shops" (e.g., La Playa, Vinos Américas)
- **MVP source discovery:**
  - LLM-assisted web search to find relevant store pages and product listings.
  - Controlled list of seed sources can be stored/configured to avoid drift.

### 2.3 Data Ingestion (Scheduled)

On each scheduled run (daily or weekly mode):

1. **Discover/refresh** a list of relevant listing/product pages for each store.
2. **Fetch** page content (HTTP fetch, optionally headless browser for JS-heavy pages).
3. **Extract** structured wine offers:
   | Field          | Description                     |
   |----------------|---------------------------------|
   | `store`        | Source store                    |
   | `product_name` | As listed on the page           |
   | `price`        | Current price in MXN            |
   | `discount`     | Discount text if visible        |
   | `volume`       | e.g., 750 ml                    |
   | `availability` | In-stock / unknown / out-of-stock|
   | `url`          | Direct product URL              |
   | `timestamp`    | When the data was captured      |
4. **Store raw snapshots** (HTML/text) and extraction payloads for audit/debugging.
5. **Dedupe/normalize** into canonical "Wine" entities (see Data Model).

### 2.4 External Reviews Enrichment (Scheduled)

For newly discovered wines and periodically for existing ones:

- Find external reviews and ratings (via LLM web search + targeted queries).
- Extract:
  - Aggregated rating (if present).
  - Key pros/cons.
  - Taste descriptors (structured tags).
  - Why opinions differ (explain disagreement patterns).
- Store both:
  - Raw review snippets/URLs (if possible).
  - Structured summary.

### 2.5 Recommendation Outputs (Scheduled)

The system generates outputs:

#### 1. Recommended Buys (per user)

- **Focus:** new wines not yet tried by that user.
- **Constraints:**
  - Strongly prefer **100–400 MXN**.
  - Allow "wow deals": exceptional quality/value outside the band.
  - **Exclude** sweet wines and non-grape wines.

#### 2. Cheapest Favorites (per user)

- Wines rated high by that user (configurable threshold, default **≥ 4**).
- List current offers sorted by total price (product price + delivery if used).

#### 3. Explanations

- Every recommendation includes a short "why" with **2–4 reasons:**
  - Similarity to liked wines.
  - Match to taste descriptors.
  - Price/value.
  - Review evidence + uncertainty if reviews conflict.

### 2.6 Tasting Feedback

- User can mark a wine as:
  - **"Tried"** (yes/no)
  - **Rating** 1–5
  - **Comment** text
- App should prompt after some time:
  - "Did you try this wine?" (manual action in UI; no push notifications required).

### 2.7 "Tried Wines" Search and Filters

- In-app searchable catalog of tried wines:
  - Search by name.
  - Filters: red/white, grape variety, name.
- Must show:
  - Personal rating history.
  - Comments.
  - Last known price/offers (optional).

### 2.8 Language

- UI supports **English** and **Russian**, toggle in UI.
- Stored content:
  - User comments: free text (any language).
  - Recommendation explanations: generated in chosen language.

---

## 3. Data Model Requirements (Relational)

### 3.1 Canonical Tables (Minimum)

#### 1. `users`

| Column        | Type      | Notes                        |
|---------------|-----------|------------------------------|
| `id`          | text      | 'A' or 'B'                  |
| `display_name`| text      |                              |
| `locale`      | text      | 'en' or 'ru'                |
| `created_at`  | timestamp |                              |

#### 2. `stores`

| Column     | Type      | Notes                              |
|------------|-----------|------------------------------------|
| `id`       | serial    | PK                                 |
| `name`     | text      |                                    |
| `category` | text      | 'supermarket' or 'specialty'       |
| `base_url` | text      |                                    |
| `enabled`  | boolean   |                                    |

#### 3. `wines` (canonical entity)

| Column          | Type       | Notes                                              |
|-----------------|------------|----------------------------------------------------|
| `id`            | serial     | PK                                                 |
| `canonical_name`| text       |                                                    |
| `producer`      | text       | nullable                                           |
| `country`       | text       | nullable                                           |
| `region`        | text       | nullable                                           |
| `type`          | text       | red/white/rosé/sparkling/other; nullable           |
| `grapes`        | text[]     | nullable                                           |
| `sweetness`     | text       | dry/off-dry/sweet; default 'unknown'               |
| `is_grape_wine` | boolean    | default true unless detected otherwise             |
| `created_at`    | timestamp  |                                                    |
| `updated_at`    | timestamp  |                                                    |

#### 4. `offers`

| Column          | Type       | Notes                                    |
|-----------------|------------|------------------------------------------|
| `id`            | serial     | PK                                       |
| `store_id`      | integer    | FK → stores                              |
| `wine_id`       | integer    | FK → wines; nullable until matched       |
| `listed_name`   | text       |                                          |
| `price_mxn`     | numeric    |                                          |
| `discount_text` | text       | nullable                                 |
| `volume_ml`     | integer    | nullable                                 |
| `availability`  | text       | in_stock / unknown / out_of_stock        |
| `product_url`   | text       |                                          |
| `captured_at`   | timestamp  |                                          |

#### 5. `price_history`

| Column       | Type       | Notes          |
|--------------|------------|----------------|
| `wine_id`    | integer    | FK → wines     |
| `store_id`   | integer    | FK → stores    |
| `price_mxn`  | numeric    |                |
| `captured_at` | timestamp |                |

#### 6. `raw_pages`

| Column        | Type       | Notes                          |
|---------------|------------|--------------------------------|
| `id`          | serial     | PK                             |
| `store_id`    | integer    | FK → stores                    |
| `url`         | text       |                                |
| `fetched_at`  | timestamp  |                                |
| `content_ref` | text       | Object storage path            |
| `content_hash`| text       |                                |
| `fetch_status`| text       |                                |

#### 7. `external_reviews`

| Column          | Type       | Notes                    |
|-----------------|------------|--------------------------|
| `id`            | serial     | PK                       |
| `wine_id`       | integer    | FK → wines               |
| `source_name`   | text       |                          |
| `source_url`    | text       |                          |
| `fetched_at`    | timestamp  |                          |
| `raw_ref`       | text       | Object storage path      |
| `extracted_json` | jsonb     |                          |

#### 8. `review_aggregates`

| Column                 | Type       | Notes                                  |
|------------------------|------------|----------------------------------------|
| `wine_id`              | integer    | FK → wines; PK                         |
| `avg_rating`           | numeric    | nullable                               |
| `rating_scale`         | text       | nullable (e.g., "100", "5", "20")      |
| `descriptors`          | jsonb      | tags + confidence                      |
| `pros`                 | jsonb      |                                        |
| `cons`                 | jsonb      |                                        |
| `disagreement_summary` | text       |                                        |
| `updated_at`           | timestamp  |                                        |

#### 9. `user_ratings`

| Column      | Type       | Notes            |
|-------------|------------|------------------|
| `id`        | serial     | PK               |
| `user_id`   | text       | FK → users       |
| `wine_id`   | integer    | FK → wines       |
| `rating_1_5`| integer    | 1–5              |
| `comment`   | text       |                  |
| `tried_at`  | date       |                  |
| `created_at`| timestamp  |                  |

#### 10. `recommendation_runs`

| Column        | Type       | Notes                              |
|---------------|------------|------------------------------------|
| `id`          | uuid       | PK (run_id)                        |
| `mode`        | text       | daily / weekly / manual            |
| `started_at`  | timestamp  |                                    |
| `finished_at` | timestamp  | nullable                           |
| `status`      | text       | success / fail                     |
| `logs_ref`    | text       | Object storage path                |

#### 11. `recommendations`

| Column              | Type       | Notes                                         |
|---------------------|------------|-----------------------------------------------|
| `run_id`            | uuid       | FK → recommendation_runs                      |
| `user_id`           | text       | FK → users                                    |
| `kind`              | text       | recommended_buys / cheapest_favorites         |
| `rank`              | integer    |                                               |
| `wine_id`           | integer    | FK → wines                                    |
| `offer_id`          | integer    | FK → offers; nullable                         |
| `score`             | numeric    |                                               |
| `explanation`       | text       |                                               |
| `explanation_locale`| text       | 'en' or 'ru'                                  |
| `created_at`        | timestamp  |                                               |

#### 12. `interaction_events` (optional, MVP+)

| Column       | Type       | Notes                                    |
|--------------|------------|------------------------------------------|
| `event_id`   | serial     | PK                                       |
| `user_id`    | text       | FK → users                               |
| `event_type` | text       | view / click / filter_change             |
| `payload`    | jsonb      |                                          |
| `created_at` | timestamp  |                                          |

### 3.2 Entity Relationship Diagram

```
users ─────────┐
               │1
               ├──────< user_ratings >──────┐
               │                             │N
               ├──────< recommendations      │
               │       (via run_id)          │
               │                             │
               └──────< interaction_events   │
                       (optional)            │
                                             │
wines ─────────────────────────────────────┘
  │1
  ├──────< offers >──────── stores
  │                            │
  ├──────< price_history ──────┘
  │
  ├──────< external_reviews
  │
  ├──────1 review_aggregates
  │
  └──────< recommendations

recommendation_runs ──────< recommendations

stores ──────< raw_pages
```

### 3.3 Dedupe/Matching Requirements

- The system must map store listings to canonical wines with:
  - String normalization + heuristics.
  - Optional LLM-assisted entity matching.
- Must be **deterministic where possible:**
  - Store `listed_name` preserved always.
  - Canonical `wine_id` assigned with match confidence.
- **If uncertain:**
  - Keep `wine_id` null or low-confidence flag.
  - Allow manual merge later (MVP may skip manual UI and just keep uncertain matches separate).

---

## 4. LLM Integration Requirements (Provider-Agnostic)

### 4.1 LLM Capabilities Needed

| Capability              | Description                                                  |
|-------------------------|--------------------------------------------------------------|
| Web search              | Tool-enabled, OR backend implements search and feeds pages   |
| Structured extraction   | Must output strict JSON according to schemas                 |
| Summarization           | Reviews with uncertainty handling                            |
| Classification          | Sweet vs. dry, wine type, basic descriptors                  |

### 4.2 Required Adapters

Implement a backend module:

**`llm_client.py`** interface with methods:

```python
class LLMClient(Protocol):
    def search(self, query: str) -> SearchResults: ...
    def extract_offers(self, page_text: str, schema: dict) -> dict: ...
    def summarize_reviews(self, texts: list[str]) -> dict: ...
    def match_wine_entity(self, listed_name: str, candidates: list[dict]) -> dict: ...
```

- Must support switching providers without rewriting business logic.

### 4.3 Prompting and Schemas

- All extraction prompts must require:
  - **JSON only** output.
  - Include **confidence** fields.
  - Include **"unknown"** rather than hallucinating.
- Store prompt templates in repo (`prompts/`) and version them.

### 4.4 Safety/Quality Guards

- Validate LLM output with **JSON schema validation**.
- **Reject/repair** invalid outputs (retry with constrained prompt).
- Log all retries and model errors.

---

## 5. Backend API Requirements

### 5.1 API Endpoints (Minimal)

| Method | Path                              | Description                                |
|--------|-----------------------------------|--------------------------------------------|
| GET    | `/health`                         | Status + last successful run timestamp     |
| POST   | `/auth/login`                     | Minimal auth                               |
| GET    | `/users/me`                       | Current user profile                       |
| GET    | `/recommendations?kind=...&date=…`| Fetch recommendations by kind and date     |
| GET    | `/favorites/cheapest`             | Cheapest offers for favorite wines         |
| GET    | `/wines/tried?query=...&filters=…`| Search/filter tried wines                  |
| POST   | `/ratings`                        | Submit rating/comment for a wine           |
| POST   | `/runs/trigger`                   | Manual pipeline run (restricted)           |

### 5.2 Auth

Since only two users, keep it simple but not silly:

| Option   | Description                                   | Recommendation      |
|----------|-----------------------------------------------|----------------------|
| Option A | Email/password with hashed passwords          | **Good for MVP**     |
| Option B | Basic auth behind a private network           | Fastest MVP          |
| Option C | OAuth                                         | Overkill for 2 users |

**Must not embed secrets in frontend.**

---

## 6. Scheduled Pipeline Requirements

### 6.1 Run Modes

| Mode     | Trigger                        |
|----------|--------------------------------|
| `daily`  | Default; runs every morning    |
| `weekly` | Friday morning local time      |
| `manual` | UI button                      |

### 6.2 Steps (Canonical)

```
┌─────────────────────────────────────────────────────┐
│                   PIPELINE STEPS                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Source discovery / refresh                       │
│         │                                           │
│         ▼                                           │
│  2. Fetch pages                                     │
│         │                                           │
│         ▼                                           │
│  3. Extract offers (LLM or deterministic parsers)   │
│         │                                           │
│         ▼                                           │
│  4. Normalize & dedupe                              │
│         │                                           │
│         ▼                                           │
│  5. Enrich with external reviews                    │
│         │                                           │
│         ▼                                           │
│  6. Score & rank                                    │
│         │                                           │
│         ▼                                           │
│  7. Write outputs                                   │
│         │                                           │
│         ▼                                           │
│  8. Write run summary + logs                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 6.3 Failure Handling

- **Partial failures must not corrupt past results.**
- If a store fetch fails:
  - Keep previous offers as historical data.
  - Flag store as "stale".
- **Retry policy:**
  - Network retries with backoff.
  - LLM retries limited (e.g., max 2 per unit).
- **Alerting:**
  - No push notifications required, but store run status for UI visibility.

---

## 7. Scoring and Recommendation Logic (Explainable)

### 7.1 Constraints (Hard Filters)

| Filter                  | Rule                                                           |
|-------------------------|----------------------------------------------------------------|
| Sweet wines             | Exclude (unless unknown and confidence low → deprioritize)     |
| Non-grape wines         | Exclude                                                        |
| Geography               | Limited to Guadalajara sources only                            |

### 7.2 Scoring Inputs

| Input                    | Weight        | Notes                                                  |
|--------------------------|---------------|--------------------------------------------------------|
| Price                    | **Dominant**  | 100–400 MXN preferred range                           |
| Discount presence/size   | Bonus         |                                                        |
| External review rating   | Bonus         | Weighted by confidence                                 |
| Descriptor match         | Bonus         | Match to user's taste profile                          |
| "Wow deal" detection     | Special bonus | Price unusually low vs. similar wines or own history   |

### 7.3 Explainability Output

Each recommendation must include **2–4 bullets** in text form explaining:

- Why it matches taste.
- Why it's good value.
- What reviews say + uncertainty.
- Why opinions differ (if applicable).

---

## 8. Frontend Requirements (Simple)

### 8.1 Pages

#### 1. Home

- **Recommended Buys** (for selected user).
- **Cheapest Favorites.**
- **Last refresh status.**

#### 2. Tried Wines

- Searchable list.
- Filters (type, grape, name).
- Wine detail with rating history.

#### 3. Add Rating

- Rate (1–5) + comment.

#### 4. Settings

- Choose active user (A/B).
- Language toggle (RU/EN).
- Schedule mode display (daily/weekly) + manual run button (optional).

### 8.2 Page Wireframes

```
┌─────────────────────────────────────────┐
│  🍷 Guadalajara Wine Finder   [A|B] [EN]│
├─────────────────────────────────────────┤
│                                         │
│  ── Recommended Buys ──────────────     │
│  ┌─────────────────────────────────┐    │
│  │ Wine Name         $250 MXN      │    │
│  │ ★★★★☆  Bodega Aurrera           │    │
│  │ • Matches your love for Malbec  │    │
│  │ • Great value at 40% off        │    │
│  │ [Rate It] [Details]             │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │ Wine Name         $180 MXN      │    │
│  │ ...                              │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ── Cheapest Favorites ────────────     │
│  ┌─────────────────────────────────┐    │
│  │ Wine Name   Your rating: ★★★★★ │    │
│  │ Cheapest: $199 @ La Playa       │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Last updated: 2026-03-13 08:00 CST     │
│  Status: ✅ Success                     │
├─────────────────────────────────────────┤
│  [Home] [Tried Wines] [Settings]        │
└─────────────────────────────────────────┘
```

### 8.3 UX Notes

- No notifications required.
- Encourage manual "did you try it?" flow.
- Keep UI responsive and minimal.

---

## 9. Logging, Artifacts, and File Policy

### 9.1 Logs

- Centralized application logs (**structured JSON logs** recommended).
- Store:
  - Pipeline step timings.
  - Number of pages fetched.
  - Number of offers extracted.
  - LLM call counts + errors.
  - Run status.
- Log storage:
  - Local file + rotation OR object storage per run (`logs/<run_id>/...`).

### 9.2 Artifacts and Raw Data

- All run outputs and one-off reports go to:
  - `artifacts/<run_id>/...`
  - **Never write directly into `artifacts/` root.**
- Raw page snapshots stored by hash:
  - `raw_pages/<yyyy-mm>/<hash>.html`

### 9.3 "No Artifacts Committed"

> No logs, no raw pages, no exports committed to Git.

`.gitignore` must include:
```
artifacts/
logs/
raw_pages/
data/
*.log
```

---

## 10. Non-Functional Requirements

### 10.1 Performance

| Metric                  | Target                                    |
|-------------------------|-------------------------------------------|
| Batch run duration      | < 30–60 minutes for MVP scale             |
| UI endpoint response    | < 1 second for normal queries             |

### 10.2 Reliability

- Scheduled runs must be **idempotent**: re-running the same run should not duplicate records incorrectly.
- Database migrations must be **versioned** (e.g., Alembic for SQLAlchemy).

### 10.3 Cost

| Item          | Target                                              |
|---------------|-----------------------------------------------------|
| **Budget**    | ~$30/month                                          |
| Cost drivers  | LLM web-search calls, page fetch volume, compute    |

**Implement quotas:**

| Quota                        | Purpose                           |
|------------------------------|-----------------------------------|
| Max pages per store per run  | Limit fetch volume                |
| Max LLM calls per run        | Limit API costs                   |
| Caching of review summaries  | Avoid redundant LLM calls         |

### 10.4 Security

- **No hardcoded credentials.**
- Secrets stored via environment variables or secret manager.
- Restrict manual-run endpoint.

---

## 11. Testing Requirements

### 11.1 Unit Tests

- Parsing utilities.
- Scoring logic.
- JSON schema validation.
- Dedupe/matching helpers.

### 11.2 Integration Tests

- Run a pipeline with recorded fixtures (mock web + mock LLM).
- Validate tables/records created properly.
- Validate API endpoints.

### 11.3 Contract Tests

- JSON schemas for extracted offers and review summaries must be validated.

---

## 12. Deliverables and Definition of Done

### 12.1 MVP Deliverables

- [ ] Working scheduled run (daily or weekly).
- [ ] UI shows:
  - [ ] Recommended Buys.
  - [ ] Cheapest Favorites.
  - [ ] Tried wines search.
- [ ] Rating submission for both users.
- [ ] Raw + normalized storage.
- [ ] Explainable recommendations.

### 12.2 Definition of Done (for a PR)

- [ ] Tests pass.
- [ ] Lint passes.
- [ ] Docs updated if behavior changed.
- [ ] No artifacts committed.
- [ ] Schemas updated if DB changed.

---

## 13. Recommended "Simplest Stack" Implementation

| Layer       | Technology                    | Notes                                       |
|-------------|-------------------------------|---------------------------------------------|
| Frontend    | Next.js or Vite + React      |                                             |
| Backend     | FastAPI + Uvicorn             |                                             |
| Database    | PostgreSQL                    | Managed or local                            |
| Scheduler   | cron + Python CLI entrypoint  |                                             |
| Storage     | S3-compatible bucket          | Optional for MVP; can start with `./data/`  |
| LLM         | Provider-agnostic adapter     | OpenAI / Anthropic / local                  |

> This stack is minimal, portable, and keeps costs predictable.

---

## Appendix A: Directory Structure (Recommended)

```
guadalajara-wine-finder/
├── frontend/                # Next.js / React app
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routes
│   │   ├── models/          # SQLAlchemy / DB models
│   │   ├── services/        # Business logic
│   │   ├── llm/             # LLM adapter layer
│   │   │   └── llm_client.py
│   │   └── pipeline/        # Scheduled batch pipeline
│   ├── prompts/             # Versioned prompt templates
│   ├── migrations/          # Alembic migrations
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   └── requirements.txt
├── data/                    # Local dev storage (gitignored)
├── artifacts/               # Run artifacts (gitignored)
├── logs/                    # Application logs (gitignored)
├── raw_pages/               # Raw page snapshots (gitignored)
├── docs/
│   └── technical-requirements-specification.md
├── docker-compose.yml       # Local dev environment
├── .env.example             # Environment variable template
├── .gitignore
└── README.md
```

## Appendix B: Environment Variables

| Variable             | Description                          | Example                              |
|----------------------|--------------------------------------|--------------------------------------|
| `DATABASE_URL`       | PostgreSQL connection string         | `postgresql://user:pass@localhost/db` |
| `LLM_PROVIDER`      | Active LLM provider                  | `openai` / `anthropic`               |
| `LLM_API_KEY`       | API key for LLM provider             | `sk-...`                             |
| `OBJECT_STORAGE_URL` | S3-compatible endpoint              | `https://s3.amazonaws.com`           |
| `OBJECT_STORAGE_KEY` | Storage access key                  | `AKIA...`                            |
| `OBJECT_STORAGE_SECRET` | Storage secret key               |                                      |
| `AUTH_SECRET`        | JWT/session secret                   |                                      |
| `RUN_MODE`           | Default run mode                     | `daily` / `weekly`                   |
| `MAX_PAGES_PER_STORE`| Quota: max pages fetched per store  | `50`                                 |
| `MAX_LLM_CALLS`     | Quota: max LLM calls per run         | `200`                                |
