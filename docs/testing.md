# Testing Guide

This document defines how to validate Guadalajara Wine Finder after changes.

## 1. Test Suite Structure

## 1.1 Unit tests

Focused logic tests without full HTTP flow:

- `tests/test_auth_unit.py`
  - password hashing/verification
  - token generation and validation
  - invalid signature/expired token handling
  - default-user bootstrap behavior
- `tests/test_llm_client_unit.py`
  - mock search result shape
  - structured offer parsing (valid + malformed rows)
  - review descriptor extraction behavior
  - entity-matching low-confidence behavior
- `tests/test_matching.py`
  - string normalization
  - overlap scoring
  - low-confidence matching branch
- `tests/test_scoring.py`
  - price band preference
  - hard filters (sweet/non-grape)
  - wow-deal/discount boost
  - explanation generation EN/RU
- `tests/test_pipeline_unit.py`
  - descriptor-match fallback and overlap branches
  - run-query success filtering

## 1.2 Integration tests

End-to-end API and pipeline behavior:

- `tests/test_api.py`
  - auth success/failure
  - protected endpoint authorization
  - recommendations flow with manual run
  - rating submit + tried wines query
  - favorites population after rating + rerun
  - frontend route serving
  - empty and forbidden states
- `tests/test_pipeline_integration.py`
  - full pipeline run
  - run summary artifact creation
  - recommendation persistence
  - idempotent rerun behavior for raw page ingestion

## 1.3 Contract tests

- `tests/test_schema_contracts.py`
  - `offers.schema.json` validity checks
  - `review_summary.schema.json` rejection behavior

## 2. Requirement-to-Test Mapping

- Parsing utilities: `test_matching.py`, `test_llm_client_unit.py`
- Scoring logic: `test_scoring.py`, `test_pipeline_unit.py`
- JSON schema validation: `test_schema_contracts.py`
- Dedupe/matching helpers: `test_matching.py`, `test_llm_client_unit.py`
- Pipeline integration with fixtures/stubs: `test_pipeline_integration.py`, `test_api.py`
- API endpoint behavior: `test_api.py`

## 3. Commands

Run lint:

- `python3 -m ruff check app tests scripts`

Run all tests:

- `python3 -m pytest -q`

Run tests with coverage report:

- `python3 -m pytest -q --cov=app --cov-report=term-missing`

Run full quality pipeline (with persisted step logs):

- `python3 scripts/run_quality_pipeline.py --base-ref HEAD~1`

Run standalone UI issue-hunt smoke checks:

- `python3 scripts/run_ui_issue_hunt.py`

Run a focused module:

- `python3 -m pytest -q tests/test_api.py`
- `python3 -m pytest -q tests/test_auth_unit.py`

## 4. CI Expectations for Done

Before merging:

1. Lint passes.
2. Tests pass.
3. Coverage report is reviewed for regressions in modified modules.
4. Documentation is updated when test scope or behavior changes.
5. Quality pipeline logs are stored for review in `artifacts/test_runs/<run_id>/`.

## 5. Runtime warning baseline

- The codebase avoids deprecated `datetime.utcnow()` usage and uses centralized UTC helpers.
- Any new deprecation warnings in quality logs should be treated as fix candidates before merge.
