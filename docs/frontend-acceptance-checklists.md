# Frontend Acceptance Checklists

## 1. Global

- [ ] User can authenticate as A or B.
- [ ] Locale toggle switches visible UI copy EN/RU without reload.
- [ ] Freshness/status is visible from Home.
- [ ] API/network errors are shown with retry action.
- [ ] Keyboard-only navigation reaches all actionable controls.

## 2. Home

- [ ] `Recommended Buys` loads from backend and preserves backend ranking.
- [ ] `Cheapest Favorites` loads and shows current best price.
- [ ] Recommendation cards show explanation text.
- [ ] Empty state appears when no run exists.
- [ ] Last successful run timestamp is shown when available.

## 3. Tried Wines

- [ ] Search by name filters results.
- [ ] Filters (type/grape) combine correctly with query.
- [ ] Rating history is visible per wine.
- [ ] Comments render safely and legibly.
- [ ] Optional last known price appears when available.
- [ ] User can delete own rating from history and item disappears after refresh.

## 4. Add Rating

- [ ] Validation blocks rating outside 1..5.
- [ ] Submit success returns visible confirmation.
- [ ] Submit failure shows clear error text.
- [ ] New rating appears in tried wines history after refresh.

## 5. Settings

- [ ] User switch updates user-bound data.
- [ ] Locale selection persists during current session.
- [ ] Locale can be saved to backend user settings and restored after login.
- [ ] Manual run action visible only for authorized user.
- [ ] Manual run feedback includes status and run id.

## 6. Localization

- [ ] All navigation labels translated EN/RU.
- [ ] Empty/error/loading messages translated EN/RU.
- [ ] No mixed-language strings in the same component state.

## 7. Accessibility

- [ ] Inputs have labels.
- [ ] Focus ring is visible for keyboard users.
- [ ] Color is not the only status signal.
- [ ] Form errors are screen-reader discoverable.

## 8. Analytics (If Enabled)

- [ ] Track page view events.
- [ ] Track recommendation card click events.
- [ ] Track filter-change events.
- [ ] Do not log secrets or comment text unless explicitly approved.

## 9. Performance

- [ ] First content render under expected threshold in local environment.
- [ ] Recommendation and tried-wines views feel responsive under normal dataset.

## 10. Anti-Requirements Validation

- [ ] No frontend LLM invocation.
- [ ] No push notification flow.
- [ ] No unrelated social features.
- [ ] No committed run artifacts/log outputs.
