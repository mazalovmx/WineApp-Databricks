# Frontend API Contract

## 1. Conventions

- Transport: HTTPS JSON.
- Auth: Bearer token from `/auth/login`.
- Time format: ISO-8601 UTC.
- Currency: MXN numeric values.
- Error shape: `{ "detail": "<message>" }`.

## 2. Authentication

## 2.1 `POST /auth/login`

Request:
- `user_id`: `"A" | "B"`
- `password`: `string`

Response:
- `access_token`: `string`
- `token_type`: `"bearer"`

Frontend rules:
- Store token in memory/session storage.
- On 401 clear token and show login state.

## 2.2 `GET /users/me`

Response:
- `id`: `"A" | "B"`
- `display_name`: `string`
- `locale`: `string`

## 2.3 `GET /users/me/settings`

Response:
- `user_id`: `"A" | "B"`
- `locale`: `"en" | "ru"`
- `updated_at`: `string`

## 2.4 `PATCH /users/me/settings`

Request:
- `locale`: `"en" | "ru"`

Response:
- `user_id`: `"A" | "B"`
- `locale`: `"en" | "ru"`
- `updated_at`: `string`

## 3. Health and Status

## 3.1 `GET /health`

Response:
- `status`: `"ok"`
- `last_successful_run`: `string | null`
- `data_freshness`: `"fresh" | "stale" | "no_successful_runs_yet"`

Frontend behavior:
- Show freshness badge globally.

## 4. Recommendations

## 4.1 `GET /recommendations?kind=<kind>&date=<optional>`

Query:
- `kind`: `recommended_buys | cheapest_favorites`
- `date`: optional string (reserved)

Response:
- `run_id`: string
- `kind`: string
- `items`: array
  - `rank`: number
  - `wine_id`: number
  - `offer_id`: number | null
  - `score`: number
  - `explanation`: string
  - `explanation_locale`: string

## 4.2 `GET /favorites/cheapest`

Equivalent to recommendations of kind `cheapest_favorites`.

## 5. Tried Wines

## 5.1 `GET /wines/tried?query=&wine_type=&grape=`

Query:
- `query`: optional string
- `wine_type`: optional string
- `grape`: optional string

Response: array of tried wine objects
- `wine_id`: number
- `canonical_name`: string
- `ratings`: array
  - `rating_id`: number
  - `rating_1_5`: number
  - `comment`: string | null
  - `tried_at`: string
- `last_known_offer_price`: number | null

## 6. Ratings

## 6.1 `POST /ratings`

Request:
- `wine_id`: number
- `rating_1_5`: 1..5
- `comment`: string | null
- `tried_at`: string | null

Response:
- `ok`: boolean
- `rating_id`: number

Frontend behavior:
- Disable submit while pending.
- Show success toast and refresh tried wines context.

## 6.2 `DELETE /ratings/{rating_id}`

Response:
- `ok`: `boolean`
- `deleted_rating_id`: `number`

Frontend behavior:
- Allow deletion only for current user owned ratings.
- Require confirmation in UI before delete.
- Refresh tried-wines panel after delete.

## 7. Manual Runs

## 7.1 `POST /runs/trigger`

Request:
- `mode`: `daily | weekly | manual`

Response:
- `run_id`: string
- `status`: `success | fail`

Auth behavior:
- 403 means user lacks permission (hide or disable trigger).

## 8. Operational Status

## 8.1 `GET /status/last-run`

Response:
- `run_id`
- `status`
- `started_at`
- `finished_at`
- `logs_ref`
- `stale_offer_count`

## 9. Frontend Data Requirements

1. Recommendations should always be requested with explicit `kind`.
2. Frontend must treat explanation text as server-owned content.
3. Client-side sorting must not alter rank semantics from backend.
4. Missing fields must render as `Unknown`, not omitted.
5. Session state (`authToken`, `activeUser`, `locale`) is client-side; locale is also persisted server-side via `/users/me/settings`.

## 10. Anti-Requirements

- No frontend endpoint assumptions beyond this contract.
- No tight coupling to mock data shapes outside documented fields.
