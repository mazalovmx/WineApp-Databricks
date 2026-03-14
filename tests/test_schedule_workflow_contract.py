from __future__ import annotations

from pathlib import Path


def test_pipeline_schedule_workflow_exists() -> None:
    workflow = Path(".github/workflows/pipeline_schedule.yml")
    assert workflow.exists()


def test_pipeline_schedule_contains_daily_and_weekly_crons() -> None:
    content = Path(".github/workflows/pipeline_schedule.yml").read_text(encoding="utf-8")
    assert 'cron: "0 6 * * *"' in content
    assert 'cron: "0 7 * * 1"' in content


def test_pipeline_schedule_runs_expected_modes() -> None:
    content = Path(".github/workflows/pipeline_schedule.yml").read_text(encoding="utf-8")
    assert "python3 scripts/run_pipeline.py --mode daily" in content
    assert "python3 scripts/run_pipeline.py --mode weekly" in content
    assert 'python3 scripts/run_pipeline.py --mode "${{ github.event.inputs.mode }}"' in content


def test_pipeline_schedule_has_manual_dispatch_with_mode_input() -> None:
    content = Path(".github/workflows/pipeline_schedule.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in content
    assert "inputs:" in content
    assert "mode:" in content
    assert "- daily" in content
    assert "- weekly" in content
    assert "- manual" in content
