"""Tests for generate_daily_briefing."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import generate_daily_briefing as briefing  # noqa: E402


def test_short_reminder_max_200_chars() -> None:
    top = [{"name": "a"}, {"name": "b"}]
    text = briefing.build_short_reminder(
        top=top,
        defer=[{"name": "c"}],
        review_open_count=1,
        current_round="round_45_daily_briefing_mvp",
    )
    assert len(text) <= 200


def test_render_includes_review_queue_section() -> None:
    template = "{{review_queue_open}}\n{{current_round}}\n"
    text = briefing.render_briefing(
        template,
        status={"repos": []},
        review_queue={
            "items": [
                {"review_id": "rq_test", "status": "open", "prompt": "Test decision"},
            ]
        },
        round_state={"current_round": "round_45", "status": "in_progress", "next_round": "round_46"},
    )
    assert "rq_test" in text
    assert "round_45" in text
