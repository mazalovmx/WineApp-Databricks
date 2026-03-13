# Repository Hygiene and Folder Review Plan

Goal: keep project structure clean, predictable, and review-friendly.

## 1) Folder ownership

- `app/` → runtime application code
- `tests/` → automated tests only
- `scripts/` → automation/ops commands
- `docs/` → project documentation
  - `docs/plans/` → reusable operational plans
  - `docs/one_time/` → temporary/one-off notes
  - `docs/` root → long-lived canonical docs
- `artifacts/` and `data/` → runtime/generated outputs (never tracked)

## 2) Hygiene checks

Run:

- `python3 scripts/repo_hygiene_check.py`

It validates:

1. top-level tracked entries stay inside allowed structure
2. no tracked runtime files under `artifacts/` or `data/`
3. temporary docs are not left in the wrong docs folder
4. required docs folders exist (`docs/plans/`, `docs/one_time/`)

## 3) Temporary docs lifecycle

1. Create temporary docs only in `docs/one_time/`.
2. Promote to permanent doc if still useful after implementation.
3. Delete obsolete one-off docs after merge/review.

## 4) Review cadence

- Run hygiene check on every PR and before every push.
- Fix structure violations before feature changes are merged.
