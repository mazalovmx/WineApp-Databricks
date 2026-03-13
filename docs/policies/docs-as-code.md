# Docs-as-Code Policy

Documentation updates are mandatory when code changes cross defined impact thresholds.

## 1) Threshold policy

A docs update is required if **any** of these are true:

1. `>= 3` code files changed
2. `>= 30` total changed code lines (additions + deletions)
3. public interface/schema changed:
   - `app/main.py`
   - `app/schemas.py`
   - `schemas/offers.schema.json`
   - `schemas/review_summary.schema.json`

## 2) What counts as docs update

At least one changed file in:

- `docs/**`, or
- `README.md`

## 3) Enforcement

Automated check:

- `python3 scripts/docs_guard.py --base-ref <ref> --head-ref HEAD`

CI workflow:

- `.github/workflows/quality_pipeline.yml`

## 4) Logging and audit trail

Every quality run stores:

- summary JSON
- per-step attempt logs
- error summary

Location:

- `artifacts/test_runs/<run_id>/...`
- `artifacts/quality_checks/...`

## 5) Operational rule

If threshold is triggered:

1. update docs immediately
2. run quality pipeline
3. commit and push code + docs together
