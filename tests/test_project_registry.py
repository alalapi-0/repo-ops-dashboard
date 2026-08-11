"""Tests for project registry sync."""

from __future__ import annotations

from pathlib import Path

import sync_project_registry as spr
import yaml


def test_project_id_normalization() -> None:
    assert spr.project_id_from_name("novel-continuation-agent") == "novel_continuation_agent"
    assert spr.project_id_from_name("repo-ops-dashboard") == "repo_ops_dashboard"


def test_build_project_meta_ops() -> None:
    project = spr.build_project(
        {
            "name": "repo-ops-dashboard",
            "path": "/tmp/repo-ops-dashboard",
            "type": "meta_ops",
            "priority_hint": "high",
            "status_hint": "bootstrap",
        }
    )
    assert project["project_id"] == "repo_ops_dashboard"
    assert project["governance_level"] == "mutation_requires_current_authority"
    assert project["default_agent"] == "Cursor"
    assert project["domain"] == "portfolio_governance"


def test_registry_file_matches_repos_count() -> None:
    root = Path(__file__).resolve().parents[1]
    repos = yaml.safe_load((root / "config" / "repos.yaml").read_text(encoding="utf-8")) or {}
    registry = yaml.safe_load((root / "governance" / "project_registry.yaml").read_text(encoding="utf-8")) or {}
    assert len(registry.get("projects", [])) == len(repos.get("repos", []))


def test_validate_projects_detects_missing_field() -> None:
    errors = spr.validate_projects([{"project_id": "x"}])
    assert errors
