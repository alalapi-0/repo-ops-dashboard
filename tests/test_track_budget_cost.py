"""Tests for budget tracking policy and tracker."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import track_budget_cost as budget  # noqa: E402
import validate_budget_tracking_policy as policy_mod  # noqa: E402


def test_policy_file_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "config" / "budget_tracking_policy.yaml"
    errors = policy_mod.validate_budget_tracking_policy_file(path)
    assert errors == []


def test_build_project_entry_active_cursor() -> None:
    registry = {"project_id": "demo", "lifecycle": "active", "default_agent": "Cursor"}
    entry = budget.build_project_entry(
        registry,
        {"lifecycle": "active", "recommended_agent": "Cursor"},
        rates={"monthly_budget_default_usd": 100.0, "per_agent_run": {"Cursor": 0.5}},
        runs_per_active=4,
        warning_pct=80.0,
    )
    assert entry["estimated_cost_usd"] == 2.0
    assert entry["budget_warning"] is False


def test_build_project_entry_warning_when_high_utilization() -> None:
    registry = {"project_id": "demo", "lifecycle": "active", "default_agent": "Codex"}
    entry = budget.build_project_entry(
        registry,
        None,
        rates={"monthly_budget_default_usd": 2.0, "per_agent_run": {"Codex": 0.5}},
        runs_per_active=4,
        warning_pct=80.0,
    )
    assert entry["budget_warning"] is True
