"""Tests for WIP limit policy and checker."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_wip_limit as wip  # noqa: E402
import validate_wip_limit_policy as policy_mod  # noqa: E402


def test_policy_file_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "config" / "wip_limit_policy.yaml"
    errors = policy_mod.validate_wip_limit_policy_file(path)
    assert errors == []


def test_active_tasks_counts_in_progress() -> None:
    queue = {
        "tasks": [
            {"task_id": "a", "status": "in_progress", "project_id": "p1"},
            {"task_id": "b", "status": "proposed", "project_id": "p2"},
            {"task_id": "c", "status": "active", "project_id": "p1"},
        ]
    }
    tasks = wip.active_tasks(queue, {"in_progress", "active"})
    assert len(tasks) == 2


def test_suggest_deferrals_when_over_limit() -> None:
    tasks = [
        {"task_id": "low", "project_id": "a", "priority": "low", "status": "in_progress"},
        {"task_id": "high", "project_id": "b", "priority": "high", "status": "in_progress"},
        {"task_id": "med", "project_id": "c", "priority": "medium", "status": "in_progress"},
    ]
    deferrals = wip.suggest_deferrals(tasks, max_wip=2, max_per_project=1)
    assert len(deferrals) == 1
    assert deferrals[0]["task_id"] == "low"


def test_build_payload_not_over_limit_with_proposed_only() -> None:
    queue = {"tasks": [{"task_id": "x", "status": "proposed", "project_id": "p", "priority": "medium"}]}
    portfolio = {"summary": {"current_wip": 0}}
    policy = {"limits": {"max_concurrent_in_progress": 2, "max_concurrent_per_project": 1, "count_statuses": ["in_progress"]}}
    payload = wip.build_payload(queue, portfolio, policy)
    assert payload["summary"]["over_limit"] is False
    assert payload["summary"]["deferral_suggestions"] == 0
