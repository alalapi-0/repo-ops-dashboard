"""Tests for priority_scoring policy and compute."""

from __future__ import annotations

from pathlib import Path

import priority_scoring as ps
import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "priority_scoring_policy.yaml"


def load_policy() -> dict:
    with POLICY_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def test_compute_priority_score_meta_ops_high() -> None:
    policy = load_policy()
    repo = {
        "type": "meta_ops",
        "status": "active",
        "health_score": 88,
        "registry_matched": True,
        "blockers": [],
        "warnings": [],
        "freeze_candidate": False,
        "archive_candidate": False,
        "round_next": "round_37_lifecycle_rules",
        "next_actions": ["继续下一轮"],
    }
    result = ps.compute_priority_score(repo, policy)
    assert result["priority_score"] >= 40
    assert result["priority_score_band"] == "high"
    breakdown = result["priority_score_breakdown"]
    assert breakdown["impact"] >= 8
    assert breakdown["unblock"] >= 6


def test_compute_priority_score_archive_low() -> None:
    policy = load_policy()
    repo = {
        "type": "unknown",
        "status": "missing",
        "health_score": 0,
        "registry_matched": False,
        "blockers": ["repository path missing"],
        "warnings": [],
        "freeze_candidate": True,
        "archive_candidate": True,
        "round_next": "",
        "next_actions": [],
    }
    result = ps.compute_priority_score(repo, policy)
    assert result["priority_score"] < 15
    assert result["priority_score_band"] == "low"
    assert result["priority_score_breakdown"]["unblock"] == 0


def test_validate_priority_scoring_policy_live_file() -> None:
    from validate_priority_scoring_policy import validate_priority_scoring_policy

    policy = load_policy()
    assert validate_priority_scoring_policy(policy, "live") == []
