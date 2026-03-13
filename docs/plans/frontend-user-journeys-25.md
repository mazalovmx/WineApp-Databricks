# Frontend Strategy: 25 User Journeys

This document describes 25 realistic user journeys and how current design/API supports each.

## A. Authentication and Session (1–5)

1. Open app first time and see Home shell, login controls, tabs.
2. Login as user A and load personalized recommendations.
3. Login as user B and verify separate personalized recommendations.
4. Switch active user control and re-authenticate for that user.
5. Logout and confirm protected data clears from session.

## B. Discovery and Recommendations (6–10)

6. View `Recommended Buys` after successful run.
7. View `Cheapest Favorites` after rating history exists.
8. Trigger manual run (user A only) and refresh recommendation blocks.
9. Observe freshness badge change (`fresh/stale/no_data`).
10. Read recommendation explanation bullets and uncertainty hints.

## C. Tried Wines and History (11–15)

11. Search tried wines by name query.
12. Filter tried wines by wine type.
13. Filter tried wines by grape.
14. Open wine detail drawer and inspect rating history timeline.
15. See last known price in tried wines table/details.

## D. Rating Lifecycle (16–20)

16. Add new rating with wine id + score + comment.
17. Add rating with explicit tasted datetime.
18. Validate rating constraints (1..5).
19. Delete own rating from tried-wines detail.
20. Confirm deleted rating no longer appears in history.

## E. User Configuration and Localization (21–25)

21. Open Settings page and see user configuration section.
22. Switch locale EN/RU and verify translated labels.
23. Persist locale in backend using save-user-settings action.
24. Reload app and confirm locale restored from user settings.
25. Verify settings run panel (mode/status/run info) remains available.

---

## Design Support Matrix

- Global shell + tabs + status badge support journeys 1, 6, 9, 21.
- Home cards and actions support journeys 6–10.
- Tried Wines table + drawer + filters support journeys 11–15, 19–20.
- Add Rating form supports journeys 16–18.
- Settings page supports journeys 21–25.
- Confirm dialog + delete button in history supports safe destructive flow (19).

## Persistence and Deletion Model

- Client session (browser):
  - `authToken`, `activeUser`, `locale` in sessionStorage.
- Backend persistence:
  - ratings/comments in `user_ratings` table,
  - user locale in `users.locale`,
  - recommendation outputs in run tables.
- User deletion capability:
  - own rating deletion via `DELETE /ratings/{rating_id}`.
  - cross-user delete blocked by authorization.
