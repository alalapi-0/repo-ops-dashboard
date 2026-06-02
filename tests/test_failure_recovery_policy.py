"""Tests for failure recovery policy and planner."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import failure_recovery as recovery  # noqa: E402
import validate_failure_recovery_policy as policy_mod  # noqa: E402


def test_policy_file_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "config/failure_recovery_policy.yaml"
    errors = policy_mod.validate_failure_recovery_policy_file(path)
    assert errors == []


def test_plan_retry_when_transient() -> None:
    root = Path(__file__).resolve().parents[1]
    policy = policy_mod.load_yaml(root / "config/failure_recovery_policy.yaml")
    plan = recovery.plan_recovery(
        task_id="task_test",
        failure_class="transient",
        retry_count=0,
        policy=policy,
    )
    assert plan["can_retry"] is True
    assert plan["action"] == "retry"
    assert str(plan["checkpoint_id"]).startswith("ckpt_")


def test_plan_hitl_after_max_retries() -> None:
    root = Path(__file__).resolve().parents[1]
    policy = policy_mod.load_yaml(root / "config/failure_recovery_policy.yaml")
    plan = recovery.plan_recovery(
        task_id="task_test",
        failure_class="transient",
        retry_count=3,
        policy=policy,
    )
    assert plan["can_retry"] is False
    assert plan["action"] == "require_hitl"
