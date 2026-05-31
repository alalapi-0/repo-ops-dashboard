"""Tests for generate_daily_brief."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import generate_daily_brief as brief  # noqa: E402


def test_pick_top_skips_archived() -> None:
    repos = [
        {"name": "a", "priority": "high", "health_score": 80, "status": "active"},
        {"name": "b", "priority": "high", "health_score": 90, "status": "missing", "archive_candidate": True},
    ]
    top = brief.pick_top_push(repos)
    assert len(top) == 1
    assert top[0]["name"] == "a"


def test_short_reminder_max_200_chars() -> None:
    top = [{"name": "x" * 50}, {"name": "y" * 50}]
    text = brief.short_reminder(top, defer=[{"name": "z"}])
    assert len(text) <= 200
