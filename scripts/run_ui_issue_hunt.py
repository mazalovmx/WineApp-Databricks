from __future__ import annotations

import argparse
import json

from app.quality import ensure_artifact_dir
from app.time_utils import utc_now_compact
from app.ui_hunt import run_ui_smoke_checks


def main() -> None:
    parser = argparse.ArgumentParser(description="Run UI smoke checks and persist logs.")
    parser.add_argument("--run-id", default=None, help="Optional shared run_id (e.g., from quality pipeline).")
    args = parser.parse_args()

    run_id = args.run_id or utc_now_compact()
    run_dir = ensure_artifact_dir("test_runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    result = run_ui_smoke_checks(run_id=run_id)
    summary = result.to_dict()

    summary_path = run_dir / "ui_issue_hunt_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log_lines = []
    for check in result.checks:
        status = "PASS" if check.success else "FAIL"
        log_lines.append(f"[{status}] {check.name}: {check.details}")
    log_path = run_dir / "ui_issue_hunt.log"
    log_path.write_text("\n".join(log_lines), encoding="utf-8")

    print(
        "ui-issue-hunt "
        f"status={summary['status']} "
        f"summary={summary_path} "
        f"log={log_path}"
    )

    if not result.success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
