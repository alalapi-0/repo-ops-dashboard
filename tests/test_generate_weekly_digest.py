"""Tests for generate_weekly_digest."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import generate_weekly_digest as digest  # noqa: E402


def test_short_reminder_max_200_chars() -> None:
    text = digest.build_short_reminder(top_names=["a", "b"], review_open_count=2, active_task_count=1)
    assert len(text) <= 200


def test_render_includes_round_state() -> None:
    template = "# Round {{current_round}}\n{{short_reminder}}\n"
    text = digest.render_digest(
        template,
        status={"repos": [{"name": "x", "priority": "high", "health_score": 80}]},
        portfolio={"summary": {"total_projects": 1, "active_projects": 1, "blocked_projects": 0}},
        review_queue={"items": []},
        task_queue={"tasks": []},
        round_state={"current_round": "round_44_test", "status": "completed", "next_round": "round_45"},
        human_notes={},
    )
    assert "round_44_test" in text
