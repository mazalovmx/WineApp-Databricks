from app.quality import evaluate_docs_policy, is_code_file, is_doc_file


def test_path_classification_helpers() -> None:
    assert is_doc_file("docs/testing.md")
    assert is_doc_file("README.md")
    assert not is_doc_file("app/main.py")
    assert is_code_file("app/main.py")
    assert is_code_file("scripts/run_pipeline.py")
    assert not is_code_file("docs/testing.md")


def test_docs_policy_does_not_require_docs_for_small_internal_change() -> None:
    changed_files = ["app/matching.py"]
    numstat = {"app/matching.py": (4, 1)}
    result = evaluate_docs_policy(changed_files, numstat, threshold_lines=30, threshold_files=3)
    assert not result.require_docs_update
    assert result.policy_pass


def test_docs_policy_requires_docs_when_threshold_hit() -> None:
    changed_files = ["app/main.py", "app/scoring.py", "scripts/run_pipeline.py"]
    numstat = {
        "app/main.py": (12, 3),
        "app/scoring.py": (5, 2),
        "scripts/run_pipeline.py": (6, 4),
    }
    result = evaluate_docs_policy(changed_files, numstat, threshold_lines=30, threshold_files=3)
    assert result.require_docs_update
    assert not result.docs_changed
    assert not result.policy_pass


def test_docs_policy_passes_when_docs_are_updated() -> None:
    changed_files = ["app/main.py", "app/schemas.py", "docs/testing.md"]
    numstat = {"app/main.py": (5, 1), "app/schemas.py": (4, 1), "docs/testing.md": (8, 0)}
    result = evaluate_docs_policy(changed_files, numstat, threshold_lines=30, threshold_files=3)
    assert result.require_docs_update
    assert result.docs_changed
    assert result.policy_pass
