"""Tests for openclaw_daily_briefing_skill."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import openclaw_daily_briefing_skill as skill  # noqa: E402


def test_short_reminder_max_200_chars() -> None:
    top = [{"name": "x" * 50}, {"name": "y" * 50}]
    text = skill.build_short_reminder(
        top=top,
        defer=[{"name": "z"}],
        review_open_count=2,
        current_round="round_58_test",
    )
    assert len(text) <= 200
    assert "OpenClaw" in text


def test_build_snapshot_includes_repo_status_fields() -> None:
    snap = skill.build_snapshot(
        status={"generated_at": "2026-06-03", "repos": [{"name": "a", "blockers": ["x"]}, {"name": "b"}]},
        round_state={"current_round": "round_58", "status": "in_progress", "next_round": "round_59"},
        review_queue={"items": [{"review_id": "r1", "status": "open", "prompt": "test"}]},
        manifest={"role": "orchestration_entry"},
        reminder="test reminder",
        digest_paths={"daily_briefing": "a.md", "weekly_digest": "b.md", "repo_status": "c.json"},
    )
    assert snap["repo_count"] == 2
    assert snap["blocked_repo_count"] == 1
    assert snap["review_queue_open_count"] == 1
    assert snap["dry_run_only"] is True
    assert snap["external_api_called"] is False


def test_excerpt_markdown_missing_file() -> None:
    text = skill.excerpt_markdown(Path("/nonexistent/daily_briefing.md"))
    assert "未找到" in text


def test_render_brief_includes_current_round(tmp_path: Path) -> None:
    daily = tmp_path / "daily.md"
    weekly = tmp_path / "weekly.md"
    daily.write_text("# Daily\nline1\n", encoding="utf-8")
    weekly.write_text("# Weekly\nline1\n", encoding="utf-8")
    template = "# Round {{current_round}}\n{{short_reminder}}\nrepos={{repo_count}}\n"
    text = skill.render_brief(
        template,
        status={"repos": [], "generated_at": "2026-06-03"},
        review_queue={"items": []},
        round_state={"current_round": "round_58_test", "status": "in_progress", "next_round": "round_59"},
        daily_briefing_path=daily,
        weekly_digest_path=weekly,
        dry_run_commands=["python3 scripts/agent_gate.py"],
    )
    assert "round_58_test" in text
    assert "repos=0" in text
