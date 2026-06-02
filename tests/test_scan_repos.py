"""Tests for scan_repos v2 core governance helpers."""

from __future__ import annotations

from pathlib import Path

import scan_repos as sr
import validate_scan_policy as vsp


def test_validate_live_scan_policy() -> None:
    root = Path(__file__).resolve().parents[1]
    data = vsp.read_scan_policy(root / "config" / "scan_policy.yaml")
    assert not vsp.validate_scan_policy(data)


def test_file_matches_pattern_glob_and_exact() -> None:
    assert sr.file_matches_pattern("round_state/current_round.yaml", "round_state/**")
    assert sr.file_matches_pattern("README.md", "README.md")
    assert not sr.file_matches_pattern("docs/index.md", "README.md")


def test_classify_read_files() -> None:
    core_policy = {
        "readme": {"patterns": ["README.md"], "required": True},
        "agents": {"patterns": ["AGENTS.md"], "required": True},
        "protocol": {"patterns": ["repo_protocol_standard.yaml"], "required": True},
        "round_state": {"patterns": ["round_state/**"], "required": False},
    }
    categories = sr.classify_read_files(
        ["README.md", "AGENTS.md", "CHANGELOG.md", "round_state/current_round.yaml"],
        core_policy,
    )
    assert categories["readme"] == ["README.md"]
    assert categories["round_state"] == ["round_state/current_round.yaml"]
    assert categories["other"] == ["CHANGELOG.md"]


def test_assess_core_governance_full_coverage() -> None:
    core_policy = {
        "readme": {"patterns": ["README.md"], "required": True},
        "agents": {"patterns": ["AGENTS.md"], "required": True},
        "protocol": {"patterns": ["repo_protocol_standard.yaml"], "required": True},
        "round_state": {"patterns": ["round_state/**"], "required": False},
    }
    summary = sr.assess_core_governance(
        ["README.md", "AGENTS.md", "repo_protocol_standard.yaml"],
        [],
        core_policy,
    )
    assert summary["required_coverage_pct"] == 100
    assert summary["missing_required_categories"] == []


def test_assess_core_governance_missing_required() -> None:
    core_policy = {
        "readme": {"patterns": ["README.md"], "required": True},
        "agents": {"patterns": ["AGENTS.md"], "required": True},
        "protocol": {"patterns": ["repo_protocol_standard.yaml"], "required": True},
        "round_state": {"patterns": ["round_state/**"], "required": False},
    }
    summary = sr.assess_core_governance(
        ["README.md"],
        ["AGENTS.md", "repo_protocol_standard.yaml"],
        core_policy,
    )
    assert summary["required_coverage_pct"] == 33
    assert "agents" in summary["missing_required_categories"]
    assert "protocol" in summary["missing_required_categories"]
