"""Tests for Feishu notification MVP (Round 56)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from send_feishu_notification import (  # noqa: E402
    apply_card_title,
    build_outbound_record,
    card_title_for_mode,
)


def test_card_title_for_mode():
    assert "日报" in card_title_for_mode("daily", None)
    assert "周报" in card_title_for_mode("weekly", None)


def test_apply_card_title():
    payload = {"card": {"header": {"title": {"tag": "plain_text", "content": "old"}}}}
    updated = apply_card_title(payload, "新标题")
    assert updated["card"]["header"]["title"]["content"] == "新标题"


def test_build_outbound_record_mock():
    record = build_outbound_record(
        mode="daily",
        payload={"msg_type": "interactive", "card": {}},
        webhook_configured=False,
        send_attempted=False,
    )
    assert record["delivery"]["status"] == "preview"
    assert record["delivery"]["webhook_configured"] is False
    assert "outbound_body" in record


def test_send_feishu_notification_dry_run_cli():
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "send_feishu_notification.py"),
            "--daily",
            str(ROOT / "reports" / "daily_repo_report.md"),
            "--status",
            str(ROOT / "data" / "repo_status.example.json"),
            "--outbound-output",
            str(ROOT / "reports" / "feishu_outbound_preview.test.json"),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env={k: v for k, v in __import__("os").environ.items() if k != "FEISHU_WEBHOOK_URL"},
    )
    assert result.returncode == 0
    out_path = ROOT / "reports" / "feishu_outbound_preview.test.json"
    assert out_path.exists()
    record = json.loads(out_path.read_text(encoding="utf-8"))
    assert record["delivery"]["status"] in {"preview", "mock"}
    out_path.unlink(missing_ok=True)
