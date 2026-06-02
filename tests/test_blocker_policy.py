"""Tests for blocker_policy and blocker_management."""

from __future__ import annotations

from pathlib import Path

import yaml

from blocker_management import classify_blocker, compute_escalation_level, enrich_blockers, summarize_blockers

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "blocker_policy.yaml"


def load_policy() -> dict:
    with POLICY_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def test_classify_governance_missing() -> None:
    policy = load_policy()
    assert classify_blocker("AGENTS.md missing", policy) == "governance_missing"


def test_classify_repository_path() -> None:
    policy = load_policy()
    assert classify_blocker("repository path missing", policy) == "repository_path"


def test_classify_repository_empty() -> None:
    policy = load_policy()
    assert classify_blocker("repository directory empty", policy) == "repository_empty"


def test_escalation_info_by_default() -> None:
    policy = load_policy()
    level = compute_escalation_level(0, policy)
    assert level["level"] == "info"
    assert level["action"] == "log_only"


def test_escalation_warning_after_3_days() -> None:
    policy = load_policy()
    level = compute_escalation_level(3, policy)
    assert level["level"] == "warning"
    assert level["action"] == "surface_in_dashboard"


def test_escalation_hitl_after_14_days() -> None:
    policy = load_policy()
    level = compute_escalation_level(14, policy)
    assert level["level"] == "hitl"
    assert level["action"] == "require_human_owner_decision"


def test_enrich_blockers_fields() -> None:
    policy = load_policy()
    details = enrich_blockers(["AGENTS.md missing"], age_days=7, policy=policy)
    assert len(details) == 1
    row = details[0]
    assert row["type"] == "governance_missing"
    assert row["escalation_level"] == "review"
    assert row["owner"] == "Cursor"


def test_summarize_blockers_max_escalation() -> None:
    policy = load_policy()
    summary = summarize_blockers(
        ["AGENTS.md missing", "repository path missing"],
        age_days=10,
        policy=policy,
    )
    assert summary["count"] == 2
    assert summary["max_escalation"] == "review"
    assert "governance_missing" in summary["types"]
    assert "repository_path" in summary["types"]


def test_validate_blocker_policy_live_file() -> None:
    from validate_blocker_policy import validate_blocker_policy

    policy = load_policy()
    assert validate_blocker_policy(policy, "live") == []
