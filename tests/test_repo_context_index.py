"""Tests for repo_context_index validation and stub builder."""

from __future__ import annotations

from pathlib import Path

import validate_repo_context_index as vrci


def test_validate_live_repo_context_index() -> None:
    root = Path(__file__).resolve().parents[1]
    data = vrci.read_repo_context_index(root / "repo_context_index.yaml")
    assert not vrci.validate_repo_context_index(data)


def test_validate_example_repo_context_index() -> None:
    root = Path(__file__).resolve().parents[1]
    data = vrci.read_repo_context_index(root / "governance" / "repo_context_index.example.yaml")
    assert not vrci.validate_repo_context_index(data)


def test_rejects_secret_like_summary() -> None:
    stub = vrci.build_repo_context_index_stub(
        project_id="demo",
        repo_name="demo",
        domain="demo",
        current_stage="active",
        summary="api_key=bad",
    )
    errors = vrci.validate_repo_context_index(stub)
    assert any("secret-like" in err for err in errors)


def test_summarize_counts_lists() -> None:
    root = Path(__file__).resolve().parents[1]
    data = vrci.read_repo_context_index(root / "repo_context_index.yaml")
    summary = vrci.summarize_repo_context_index(data)
    assert summary["key_files_count"] >= 4
    assert summary["project_id"] == "repo_ops_dashboard"
