"""Tests for analyze_repos core logic."""

from __future__ import annotations

import analyze_repos as ar


def test_derive_blockers_missing_critical_files() -> None:
    repo = {
        "status": "active",
        "missing": ["AGENTS.md", "docs/optional.md"],
    }
    assert ar.derive_blockers(repo) == ["AGENTS.md missing"]


def test_derive_blockers_missing_path() -> None:
    repo = {"status": "missing", "missing": []}
    assert ar.derive_blockers(repo) == ["repository path missing"]


def test_derive_blockers_empty_directory() -> None:
    repo = {"status": "empty"}
    assert ar.derive_blockers(repo) == ["repository directory empty"]


def test_derive_lifecycle_archived() -> None:
    repo = {"status": "active", "archive_candidate": True}
    assert ar.derive_lifecycle(repo) == "archived"


def test_compute_health_active_repo() -> None:
    weights = {
        "readme_exists": 10,
        "agents_exists": 15,
        "protocol_exists": 15,
        "changelog_exists": 5,
        "round_state_exists": 10,
        "docs_index_exists": 10,
        "recent_update": 10,
        "has_next_action": 10,
        "no_blocker": 15,
    }
    repo = {
        "status": "active",
        "read_files": [
            "README.md",
            "AGENTS.md",
            "repo_protocol_standard.yaml",
            "CHANGELOG.md",
            "round_state/current_round.yaml",
            "docs/index.md",
        ],
        "missing": [],
        "warnings": [],
    }
    score = ar.compute_health(repo, weights)
    assert score >= 70


def test_pick_priority_high_for_meta_ops() -> None:
    repo = {"status": "active", "type": "meta_ops", "priority_hint": ""}
    assert ar.pick_priority(repo, health_score=50) == "high"


def test_pick_priority_low_for_missing() -> None:
    repo = {"status": "missing", "type": "unknown"}
    assert ar.pick_priority(repo, health_score=0) == "low"


def test_recommend_agent_archive_candidate() -> None:
    assert ar.recommend_agent("high", [], "novel_agent", archive_candidate=True) == "Human"


def test_recommend_agent_meta_ops() -> None:
    assert ar.recommend_agent("medium", [], "meta_ops", archive_candidate=False) == "Cursor"
