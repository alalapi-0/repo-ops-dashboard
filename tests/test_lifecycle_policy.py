"""Tests for lifecycle_policy and derive_lifecycle."""

from __future__ import annotations

from pathlib import Path

import analyze_repos as ar
import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "lifecycle_policy.yaml"


def load_policy() -> dict:
    with POLICY_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def test_derive_lifecycle_archived() -> None:
    policy = load_policy()
    repo = {"status": "active", "archive_candidate": True}
    assert ar.derive_lifecycle_v1(repo, policy=policy) == "archived"


def test_derive_lifecycle_blocked() -> None:
    policy = load_policy()
    repo = {"status": "active", "blockers": ["AGENTS.md missing"]}
    assert ar.derive_lifecycle_v1(repo, policy=policy) == "blocked"


def test_derive_lifecycle_frozen() -> None:
    policy = load_policy()
    repo = {"status": "active", "freeze_candidate": True}
    assert ar.derive_lifecycle_v1(repo, policy=policy) == "frozen"


def test_derive_lifecycle_maintenance_low_health() -> None:
    policy = load_policy()
    repo = {"status": "active", "freeze_candidate": False, "archive_candidate": False}
    assert ar.derive_lifecycle_v1(repo, health_score=25, registry_matched=True, policy=policy) == "maintenance"


def test_derive_lifecycle_idea_unmatched() -> None:
    policy = load_policy()
    repo = {"status": "active", "freeze_candidate": False, "archive_candidate": False}
    assert ar.derive_lifecycle_v1(repo, health_score=80, registry_matched=False, policy=policy) == "idea"


def test_validate_lifecycle_policy_live_file() -> None:
    from validate_lifecycle_policy import validate_lifecycle_policy

    policy = load_policy()
    assert validate_lifecycle_policy(policy, "live") == []
