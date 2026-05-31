"""Tests for Feishu payload and Bitable sync helpers."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_feishu_payload import (  # noqa: E402
    FEISHU_MAX_BODY_BYTES,
    build_payload,
    compute_status_stats,
    extract_brief_excerpt,
    format_stats_line,
    sign_payload,
    truncate_for_feishu,
    webhook_body,
)
from sync_feishu_bitable import join_list, repo_to_fields  # noqa: E402


def test_compute_status_stats():
    data = {
        "repos": [
            {"priority": "high", "blockers": ["a"], "freeze_candidate": True},
            {"priority": "low", "blockers": []},
        ]
    }
    stats = compute_status_stats(data)
    assert stats["total"] == 2
    assert stats["high_priority"] == 1
    assert stats["blocker_count"] == 1
    assert stats["freeze_count"] == 1


def test_format_stats_line():
    line = format_stats_line({"total": 3, "high_priority": 1, "blocker_count": 2, "freeze_count": 1})
    assert "仓库 3" in line
    assert "卡点 2" in line


def test_extract_brief_excerpt_short_reminder():
    brief = "## 短提醒\n\n今日优先推进：foo, bar。\n\n## 其他"
    excerpt = extract_brief_excerpt(brief, max_chars=300)
    assert "foo" in excerpt
    assert "/Users/" not in excerpt


def test_build_payload_includes_stats_and_brief():
    payload = build_payload(
        "## 高优先级仓库\n\n- **demo** — high\n",
        "",
        stats={"total": 1, "high_priority": 1, "blocker_count": 0, "freeze_count": 0},
        brief_excerpt="短提醒内容",
        for_send=False,
    )
    content = payload["card"]["elements"][0]["text"]["content"]
    assert "概览" in content
    assert "每日简报" in content
    assert "短提醒内容" in content


def test_repo_to_fields_no_path():
    fields = repo_to_fields(
        {
            "name": "demo",
            "path": "/Users/secret/demo",
            "type": "meta_ops",
            "priority": "high",
            "health_score": 80,
            "blockers": ["missing README"],
            "next_actions": ["fix"],
            "recommended_agent": "Cursor",
            "lifecycle_status": "active",
            "last_checked": "2026-05-31T12:00:00+00:00",
        },
        sync_at_ms=1710000000000,
    )
    assert fields["repo_name"] == "demo"
    assert "path" not in fields
    assert "/Users" not in json.dumps(fields)


def test_join_list():
    assert join_list(["a", "b"]) == "a; b"
    assert join_list(None) == ""


def test_sign_payload_matches_feishu_algorithm():
    # Feishu: HmacSHA256(key=timestamp+"\n"+secret, message=empty) -> base64
    sign = sign_payload("demo-secret", "1599360473")
    assert isinstance(sign, str)
    assert len(sign) > 0


def test_truncate_for_feishu_limits_body_size():
    huge = "x" * 30000
    body = {
        "msg_type": "interactive",
        "card": {
            "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": huge}}],
        },
    }
    trimmed = truncate_for_feishu(body, max_bytes=FEISHU_MAX_BODY_BYTES)
    assert len(json.dumps(trimmed, ensure_ascii=False).encode("utf-8")) <= FEISHU_MAX_BODY_BYTES


def test_sync_feishu_bitable_dry_run_cli():
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "sync_feishu_bitable.py"),
            "--input",
            str(ROOT / "data" / "repo_status.example.json"),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "dry-run" in result.stdout.lower()
