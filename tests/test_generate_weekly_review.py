"""Tests for generate_weekly_review."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import generate_weekly_review as wr  # noqa: E402


def test_format_human_section_empty() -> None:
    text = wr.format_human_section({})
    assert "human_notes.json" in text


def test_build_review_contains_sections() -> None:
    review = wr.build_review(
        priority_text="# Priority\n",
        brief_text="# Brief\n",
        weekly_text="# Weekly\n",
        human_notes={"week_label": "2026-W01", "notes": ["a"], "focus_repos": []},
    )
    assert "Weekly Review" in review
    assert "Human 本周笔记" in review
    assert "优先级复盘摘要" in review
