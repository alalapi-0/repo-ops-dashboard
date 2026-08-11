"""Tests for Feishu notification planning (Round 55)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from plan_feishu_notifications import build_plan, source_readiness  # noqa: E402
from validate_feishu_notification_policy import (  # noqa: E402
    load_yaml,
    validate_feishu_notification_policy,
)


def test_validate_feishu_notification_policy_ok():
    path = ROOT / "config" / "feishu_notification_policy.yaml"
    errors = validate_feishu_notification_policy(load_yaml(path), source=path.name)
    assert errors == []


def test_source_readiness_tracks_exists():
    policy = load_yaml(ROOT / "config" / "feishu_notification_policy.yaml")
    readiness = source_readiness(ROOT, policy.get("sources", {}))
    assert "daily_report" in readiness
    assert isinstance(readiness["daily_report"]["exists"], bool)


def test_build_plan_no_external_api():
    policy = load_yaml(ROOT / "config" / "feishu_notification_policy.yaml")
    plan = build_plan(ROOT, policy)
    assert plan["external_api_called"] is False
    assert plan["mode"] == "planning_only"
    assert "summary" in plan


def test_plan_feishu_notifications_cli_dry_run():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "plan_feishu_notifications.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "planning" in result.stdout.lower() or "plan" in result.stdout.lower()


def test_plan_feishu_notifications_write(tmp_path: Path):
    plan_path = tmp_path / "plan.yaml"
    report_path = tmp_path / "report.md"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "plan_feishu_notifications.py"),
            "--write",
            "--output-plan",
            str(plan_path),
            "--output-report",
            str(report_path),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert plan_path.exists()
    assert report_path.exists()
