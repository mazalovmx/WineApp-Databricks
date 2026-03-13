# Full Testing and Issue-Hunt Plan

This is the execution plan for finding backend and UI issues systematically.

## 1) Backend test plan

1. Run static checks:
   - `python3 -m ruff check app tests scripts`
2. Run full automated tests:
   - `python3 -m pytest -q`
3. Run coverage review:
   - `python3 -m pytest -q --cov=app --cov-report=term-missing`
4. Run data seeding validation:
   - `python3 scripts/seed_demo_data.py --wines 45`
5. Review generated logs:
   - `artifacts/test_runs/<run_id>/summary.json`
   - `artifacts/test_runs/<run_id>/errors.log`
   - step logs `*_attempt_<n>.log`

## 2) UI issue-hunt plan (manual)

1. Start server:
   - `python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
2. Verify flows for user A and B:
   - Login/logout
   - Home (status + recommendations)
   - Tried Wines (search/filter/open details)
   - Add Rating (validation + submit)
   - Settings (manual run permissions + status)
3. Switch EN/RU and verify:
   - labels and buttons translate
   - visual layout remains consistent
4. Capture artifacts:
   - one demo video
   - key screenshots (home, tried, settings)

## 3) Defect triage

1. Severity:
   - S1: data loss/security/auth bypass
   - S2: incorrect recommendations/pricing output
   - S3: non-blocking UI/API regressions
2. Each failure must include:
   - reproduction steps
   - command or route
   - expected vs actual
   - log file path

## 4) Exit criteria

- lint passes
- tests pass
- coverage reviewed
- critical/manual flows validated
- logs persisted for audit
