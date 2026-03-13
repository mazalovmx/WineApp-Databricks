# Frontend Information Architecture

## 1. Product Truths (Non-Negotiable)

1. App serves exactly two identities: `A` and `B`.
   - `A`: Alexander
   - `B`: Elena
2. Geography scope is Guadalajara, Jalisco sources only.
3. Main outcomes are:
   - `Recommended Buys` (new wines for user, value-focused).
   - `Cheapest Favorites` (already liked wines, best current price).
4. Frontend is read-mostly over batch-prepared backend outputs.
5. Runtime LLM calls from frontend are forbidden.
6. RU/EN language toggle is required and must not require page reload.

## 2. Navigation Model

Top-level destinations:
1. **Home**
2. **Tried Wines**
3. **Add Rating**
4. **Settings**

Global persistent controls:
- Active user switch (`A` / `B`)
- Locale switch (`EN` / `RU`)
- Data freshness indicator

## 3. Route Map

- `/` → Home dashboard
- `/tried` → Tried wines list + filters + detail panel
- `/ratings/new` → Rating submission
- `/settings` → User/locale preferences + run controls

No hidden pages. No admin panel.

## 4. Page Goals and Content Priority

### 4.1 Home
Priority order:
1. Last refresh / pipeline health
2. Recommended Buys list
3. Cheapest Favorites list
4. Quick actions (rate wine, open tried wines)

### 4.2 Tried Wines
Priority order:
1. Search input
2. Filters: type, grape, name
3. Results list
4. Wine detail (rating history, comments, optional last known price)

### 4.3 Add Rating
Priority order:
1. Wine selector/input
2. Tried confirmation
3. Rating 1–5
4. Optional comment
5. Submit state and success/failure feedback

### 4.4 Settings
Priority order:
1. Active user selection
2. Locale toggle
3. Schedule mode display
4. Manual run trigger (if authorized)

## 5. Information Hierarchy Rules

1. Critical pipeline status is always visible on Home above recommendation content.
2. Recommendation entries always show:
   - wine name
   - effective price
   - short explanation (2–4 bullets)
3. Unknown/missing data is rendered explicitly as `Unknown`, never blank.
4. Error states must be actionable and non-technical.

## 6. Cross-Page State

Persistent client state:
- `activeUser` (`A` or `B`)
- `locale` (`en` or `ru`)
- `authToken` (session scoped)

Derived state:
- `lastSuccessfulRun`
- `isDataStale`
- `manualRunAllowed` (user A only)

Persisted server-side user settings:
- `locale` via `/users/me/settings`

## 7. Empty/Error/Loading States

- Loading: skeleton rows for lists; spinner for submit actions.
- Empty:
  - No recommendations yet → show run trigger guidance.
  - No tried wines → prompt to add first rating.
- Error:
  - Auth failure: clear token and redirect to login state.
  - API unavailable: show retry action and last-known refresh age.

Destructive action support:
- User can delete own rating entries from Tried Wines detail view.
- Delete action requires explicit confirmation before API call.

## 8. Anti-Requirements

Do not implement:
- social feeds
- push notifications
- real-time streaming recommendations
- in-frontend scraping or LLM calls
- map/location browsing
