from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

DOC_PATH_PREFIXES = ("docs/",)
DOC_FILES = {"README.md"}
CODE_PATH_PREFIXES = ("app/", "scripts/", "schemas/", "prompts/", "tests/")
CODE_SUFFIXES = (".py", ".json", ".md", ".html", ".css", ".js")
PUBLIC_INTERFACE_FILES = {
    "app/main.py",
    "app/schemas.py",
    "schemas/offers.schema.json",
    "schemas/review_summary.schema.json",
}
TRACKED_RUNTIME_DIRS = {"artifacts/", "data/"}


@dataclass(slots=True)
class DocsPolicyResult:
    docs_changed: bool
    code_files_changed: int
    code_lines_changed: int
    changed_public_interface: bool
    require_docs_update: bool
    policy_pass: bool
    reasons: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def is_doc_file(path: str) -> bool:
    return path in DOC_FILES or path.startswith(DOC_PATH_PREFIXES)


def is_code_file(path: str) -> bool:
    if not path.startswith(CODE_PATH_PREFIXES):
        return False
    return path.endswith(CODE_SUFFIXES)


def evaluate_docs_policy(
    changed_files: list[str],
    numstat: dict[str, tuple[int, int]],
    *,
    threshold_lines: int = 30,
    threshold_files: int = 3,
) -> DocsPolicyResult:
    docs_changed = any(is_doc_file(path) for path in changed_files)
    code_files = [path for path in changed_files if is_code_file(path)]
    code_files_changed = len(code_files)
    code_lines_changed = sum(sum(numstat.get(path, (0, 0))) for path in code_files)
    changed_public_interface = any(path in PUBLIC_INTERFACE_FILES for path in changed_files)

    reasons: list[str] = []
    require_docs = False

    if code_files_changed >= threshold_files:
        require_docs = True
        reasons.append(
            f"code file count threshold reached ({code_files_changed} >= {threshold_files})"
        )
    if code_lines_changed >= threshold_lines:
        require_docs = True
        reasons.append(
            f"code line threshold reached ({code_lines_changed} >= {threshold_lines})"
        )
    if changed_public_interface:
        require_docs = True
        reasons.append("public interface/schema files changed")

    policy_pass = (not require_docs) or docs_changed
    if require_docs and not docs_changed:
        reasons.append("required docs update missing for this change set")

    return DocsPolicyResult(
        docs_changed=docs_changed,
        code_files_changed=code_files_changed,
        code_lines_changed=code_lines_changed,
        changed_public_interface=changed_public_interface,
        require_docs_update=require_docs,
        policy_pass=policy_pass,
        reasons=reasons,
    )


def ensure_artifact_dir(subdir: str) -> Path:
    base = Path("artifacts") / subdir
    base.mkdir(parents=True, exist_ok=True)
    return base
