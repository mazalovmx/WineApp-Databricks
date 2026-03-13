from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from app.quality import ensure_artifact_dir
from app.time_utils import utc_now_compact, utc_now_iso


@dataclass(slots=True)
class StepAttempt:
    attempt: int
    command: str
    return_code: int
    log_path: str
    started_at: str
    finished_at: str


@dataclass(slots=True)
class StepResult:
    name: str
    command: str
    max_attempts: int
    attempts: list[StepAttempt]

    @property
    def success(self) -> bool:
        return any(a.return_code == 0 for a in self.attempts)


def _run_step(
    run_dir: Path,
    name: str,
    command: str,
    *,
    max_attempts: int = 1,
) -> StepResult:
    attempts: list[StepAttempt] = []
    for attempt in range(1, max_attempts + 1):
        started = utc_now_iso()
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
        )
        finished = utc_now_iso()

        log_path = run_dir / f"{name}_attempt_{attempt}.log"
        text = "\n".join(
            [
                f"step={name}",
                f"attempt={attempt}",
                f"command={command}",
                f"return_code={completed.returncode}",
                "--- stdout ---",
                completed.stdout or "",
                "--- stderr ---",
                completed.stderr or "",
            ]
        )
        log_path.write_text(text, encoding="utf-8")
        attempts.append(
            StepAttempt(
                attempt=attempt,
                command=command,
                return_code=completed.returncode,
                log_path=str(log_path),
                started_at=started,
                finished_at=finished,
            )
        )
        if completed.returncode == 0:
            break
    return StepResult(name=name, command=command, max_attempts=max_attempts, attempts=attempts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run quality pipeline with persisted logs.")
    parser.add_argument("--base-ref", default="HEAD~1")
    parser.add_argument("--pytest-retries", type=int, default=1)
    args = parser.parse_args()

    run_id = utc_now_compact()
    run_root = ensure_artifact_dir("test_runs")
    run_dir = run_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    step_specs = [
        ("repo_hygiene", "python3 scripts/repo_hygiene_check.py", 1),
        (
            "docs_guard",
            f"python3 scripts/docs_guard.py --base-ref {args.base_ref} --head-ref HEAD",
            1,
        ),
        ("lint", "python3 -m ruff check app tests scripts", 1),
        ("tests", "python3 -m pytest -q", max(args.pytest_retries, 1)),
        (
            "coverage",
            "python3 -m pytest -q --cov=app --cov-report=term-missing",
            max(args.pytest_retries, 1),
        ),
    ]

    results: list[StepResult] = []
    for name, cmd, attempts in step_specs:
        result = _run_step(run_dir, name, cmd, max_attempts=attempts)
        results.append(result)

    failed = [step for step in results if not step.success]
    summary = {
        "run_id": run_id,
        "started_at": results[0].attempts[0].started_at if results else utc_now_iso(),
        "finished_at": utc_now_iso(),
        "status": "success" if not failed else "fail",
        "steps": [
            {
                "name": step.name,
                "command": step.command,
                "max_attempts": step.max_attempts,
                "success": step.success,
                "attempts": [asdict(attempt) for attempt in step.attempts],
            }
            for step in results
        ],
    }

    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    errors_path = run_dir / "errors.log"
    if failed:
        lines = ["Quality pipeline failures:"]
        for step in failed:
            last = step.attempts[-1]
            lines.append(
                f"- {step.name} failed after {len(step.attempts)} attempt(s), "
                f"log={last.log_path}, return_code={last.return_code}"
            )
        errors_path.write_text("\n".join(lines), encoding="utf-8")
    else:
        errors_path.write_text("No failures detected.", encoding="utf-8")

    print(
        "quality-pipeline "
        f"status={summary['status']} "
        f"summary={summary_path} "
        f"errors={errors_path}"
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
