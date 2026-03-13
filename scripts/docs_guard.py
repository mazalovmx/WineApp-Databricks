from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime

from app.quality import ensure_artifact_dir, evaluate_docs_policy


def _run_git_command(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _changed_files(base_ref: str, head_ref: str) -> list[str]:
    output = _run_git_command(["diff", "--name-only", f"{base_ref}...{head_ref}"])
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def _numstat(base_ref: str, head_ref: str) -> dict[str, tuple[int, int]]:
    output = _run_git_command(["diff", "--numstat", f"{base_ref}...{head_ref}"])
    result: dict[str, tuple[int, int]] = {}
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add_raw, del_raw, path = parts
        added = int(add_raw) if add_raw.isdigit() else 0
        deleted = int(del_raw) if del_raw.isdigit() else 0
        result[path] = (added, deleted)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Docs-as-code threshold guard.")
    parser.add_argument("--base-ref", default="HEAD~1")
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--threshold-lines", type=int, default=30)
    parser.add_argument("--threshold-files", type=int, default=3)
    args = parser.parse_args()

    changed = _changed_files(args.base_ref, args.head_ref)
    diff_numstat = _numstat(args.base_ref, args.head_ref)
    result = evaluate_docs_policy(
        changed,
        diff_numstat,
        threshold_lines=args.threshold_lines,
        threshold_files=args.threshold_files,
    )

    payload = {
        "base_ref": args.base_ref,
        "head_ref": args.head_ref,
        "timestamp": datetime.utcnow().isoformat(),
        "changed_files": changed,
        "numstat": {k: {"added": v[0], "deleted": v[1]} for k, v in diff_numstat.items()},
        "policy": result.to_dict(),
    }

    out_dir = ensure_artifact_dir("quality_checks")
    out_path = out_dir / f"docs_guard_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(
        "docs-guard "
        f"pass={result.policy_pass} "
        f"require_docs_update={result.require_docs_update} "
        f"docs_changed={result.docs_changed} "
        f"code_files_changed={result.code_files_changed} "
        f"code_lines_changed={result.code_lines_changed} "
        f"report={out_path}"
    )
    if result.reasons:
        print("reasons:")
        for reason in result.reasons:
            print(f"- {reason}")

    if not result.policy_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
