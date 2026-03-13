from __future__ import annotations

import json
import subprocess
from pathlib import Path

from app.quality import TRACKED_RUNTIME_DIRS, ensure_artifact_dir
from app.time_utils import utc_now_compact, utc_now_iso

TOP_LEVEL_ALLOWED = {
    ".github",
    ".env.example",
    ".gitignore",
    "README.md",
    "pyproject.toml",
    "app",
    "docs",
    "prompts",
    "schemas",
    "scripts",
    "tests",
}

TEMP_DOC_MARKERS = ("temp", "draft", "wip", "scratch", "oneoff", "one-off")


def _tracked_files() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    return lines


def _top_level_unknown_entries(tracked_files: list[str]) -> list[str]:
    top_levels = sorted({path.split("/", 1)[0] for path in tracked_files})
    return [entry for entry in top_levels if entry not in TOP_LEVEL_ALLOWED]


def _runtime_dirs_tracked_files(tracked_files: list[str]) -> list[str]:
    offenders: list[str] = []
    runtime_prefixes = tuple(TRACKED_RUNTIME_DIRS)
    for path in tracked_files:
        if path.startswith(runtime_prefixes):
            offenders.append(path)
    return offenders


def _misplaced_temp_docs(tracked_files: list[str]) -> list[str]:
    offenders: list[str] = []
    for path in tracked_files:
        lowered = path.lower()
        if not lowered.startswith("docs/") or not lowered.endswith(".md"):
            continue
        if lowered.startswith("docs/one_time/"):
            continue
        if any(marker in Path(path).stem.lower() for marker in TEMP_DOC_MARKERS):
            offenders.append(path)
    return offenders


def main() -> None:
    tracked = _tracked_files()
    unknown_top = _top_level_unknown_entries(tracked)
    runtime_tracked = _runtime_dirs_tracked_files(tracked)
    temp_misplaced = _misplaced_temp_docs(tracked)

    docs_one_time_exists = Path("docs/one_time").exists()
    docs_plans_exists = Path("docs/plans").exists()

    checks = {
        "unknown_top_level_entries": unknown_top,
        "tracked_runtime_files": runtime_tracked,
        "misplaced_temp_docs": temp_misplaced,
        "docs_one_time_exists": docs_one_time_exists,
        "docs_plans_exists": docs_plans_exists,
    }
    failures = {
        key: value
        for key, value in checks.items()
        if (isinstance(value, list) and value) or (isinstance(value, bool) and not value)
    }

    payload = {
        "timestamp": utc_now_iso(),
        "checks": checks,
        "status": "pass" if not failures else "fail",
    }

    out_dir = ensure_artifact_dir("quality_checks")
    out_path = out_dir / f"repo_hygiene_{utc_now_compact()}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"repo-hygiene status={payload['status']} report={out_path}")
    if failures:
        for key, value in failures.items():
            print(f"- {key}: {value}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
