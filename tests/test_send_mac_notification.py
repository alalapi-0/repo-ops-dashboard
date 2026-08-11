"""Tests for Mac local notification (Round 57)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from send_mac_notification import (  # noqa: E402
    build_payload,
    collect_blockers,
    extract_brief_excerpt,
    should_skip_osascript,
)
from validate_mac_notification_policy import (  # noqa: E402
    load_yaml,
    validate_mac_notification_policy,
)


def test_validate_mac_notification_policy_ok():
    path = ROOT / "config" / "mac_notification_policy.yaml"
    errors = validate_mac_notification_policy(load_yaml(path), source=path.name)
    assert errors == []


def test_extract_brief_excerpt():
    brief = "## 短提醒\n\n今日优先：repo-a。\n\n## 其他"
    excerpt = extract_brief_excerpt(brief)
    assert "repo-a" in excerpt
    assert "/Users/" not in excerpt


def test_collect_blockers():
    data = {"repos": [{"name": "demo", "blockers": ["missing README"]}, {"name": "ok", "blockers": []}]}
    items = collect_blockers(data)
    assert len(items) == 1
    assert "demo" in items[0]


def test_build_payload_dry_run():
    policy = load_yaml(ROOT / "config" / "mac_notification_policy.yaml")
    payload = build_payload(policy=policy, brief_excerpt="今日推进 A", blockers=[], for_send=False)
    assert payload["delivery"]["status"] == "dry_run"
    assert payload["notification"]["title"] == "Repo Ops"


def test_send_mac_notification_cli_write_to_temp(tmp_path: Path):
    payload_path = tmp_path / "payload.json"
    report_path = tmp_path / "report.md"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "send_mac_notification.py"),
            "--status",
            str(ROOT / "data" / "repo_status.example.json"),
            "--write",
            "--output",
            str(payload_path),
            "--report",
            str(report_path),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert payload_path.exists()
    assert report_path.exists()
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    assert payload["delivery"]["status"] == "dry_run"


def test_send_mac_notification_default_is_non_mutating(tmp_path: Path):
    payload_path = tmp_path / "payload.json"
    report_path = tmp_path / "report.md"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "send_mac_notification.py"),
            "--status",
            str(ROOT / "data" / "repo_status.example.json"),
            "--output",
            str(payload_path),
            "--report",
            str(report_path),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "rendered in memory" in result.stdout
    assert not payload_path.exists()
    assert not report_path.exists()
