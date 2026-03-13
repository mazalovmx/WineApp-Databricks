# Frontend Component Specification

## 1. Component Inventory

## 1.1 App Shell

### `AppShell`
- Responsibility: global layout, nav, locale/user controls, auth gate.
- Inputs: `activeUser`, `locale`, `health`.
- Outputs/events: `onUserChange`, `onLocaleChange`, `onLogout`.

### `TopNav`
- Tabs: Home, Tried Wines, Add Rating, Settings.
- Accessibility: keyboard arrow/tab reachable.

### `StatusBadge`
- Displays `fresh`, `stale`, or `no_data`.
- Must include text label and color cue.

## 1.2 Home

### `RecommendationList`
- Props:
  - `kind`: `recommended_buys | cheapest_favorites`
  - `items: RecommendationItem[]`
  - `isLoading`
  - `error`
- Renders `RecommendationCard` list.

### `RecommendationCard`
- Fields:
  - wine name
  - store (if available)
  - total price (MXN)
  - explanation bullets (2–4)
  - uncertainty marker if conflicting reviews

### `RunSummaryPanel`
- Shows last successful run timestamp and freshness.
- Optional manual run button when authorized.

## 1.3 Tried Wines

### `TriedWineFilters`
- Controls:
  - text search
  - type filter (red/white/rose/sparkling/other)
  - grape filter

### `TriedWineTable`
- Columns:
  - name
  - last rating
  - number of ratings
  - optional last known price

### `WineHistoryDrawer`
- Displays rating history timeline and comments for selected wine.
- Includes per-entry delete action for owned ratings with confirm step.

## 1.4 Add Rating

### `RatingForm`
- Inputs:
  - `wine_id` (required)
  - `rating_1_5` (required)
  - `comment` (optional)
  - `tried_at` (optional)
- Validation:
  - rating 1..5
  - wine id positive integer

## 1.5 Settings

### `UserSwitcher`
- Values: `A`, `B`
- On change refreshes user-bound recommendation queries.

### `LocaleSwitcher`
- Values: `en`, `ru`
- Must switch labels and generated explanation language requests.
- Locale can be persisted for the current user from Settings page.

### `ManualRunButton`
- Visible only when user has permission.
- States: idle/loading/success/error.

### `UserSettingsSaveButton`
- Saves current locale to backend user profile.
- States: idle/loading/success/error.

## 2. Shared Utilities

### `ApiClient`
- Handles bearer token injection.
- Normalizes API errors.
- Provides typed request/response wrappers.

### `I18n`
- Key-based dictionaries for EN and RU.
- Required fallback to EN for missing keys.

## 3. State Boundaries

- Server state: recommendations, health, tried wines, ratings history.
- Server state also includes user locale preference.
- Client state: active tab, selected wine, locale, user.
- Never duplicate server truth in multiple stores.

## 4. Accessibility Requirements

1. All interactive controls keyboard reachable.
2. Focus styles visible.
3. Inputs have programmatic labels.
4. Contrast ratio meets WCAG AA (text and controls).
5. Errors announced via ARIA live region for form submits.

## 5. Anti-Requirements

Do not add:
- custom charting libraries
- complex drag-and-drop
- modal-heavy flows where inline forms are enough
- hidden power-user controls
