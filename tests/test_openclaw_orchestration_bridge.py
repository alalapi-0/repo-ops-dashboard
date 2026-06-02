"""Tests for openclaw_orchestration_bridge."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import openclaw_orchestration_bridge as bridge  # noqa: E402


def test_pick_top_skips_frozen() -> None:
    projects = [
        {"project_id": "a", "priority": "high", "lifecycle": "active", "repo_name": "a"},
        {"project_id": "b", "priority": "high", "lifecycle": "frozen", "repo_name": "b"},
    ]
    top = bridge.pick_top_projects(projects)
    assert len(top) == 1
    assert top[0]["project_id"] == "a"


def test_short_reminder_max_200_chars() -> None:
    top = [{"repo_name": "x" * 50, "project_id": "x"}, {"repo_name": "y" * 50, "project_id": "y"}]
    text = bridge.build_short_reminder(
        top=top,
        defer=[{"project_id": "z"}],
        review_open_count=3,
        current_round="round_43_openclaw_orchestration_bridge",
    )
    assert len(text) <= 200


def test_render_brief_includes_current_round() -> None:
    template = "# Round {{current_round}}\n{{short_reminder}}\n"
    text = bridge.render_brief(
        template,
        portfolio={"summary": {"total_projects": 1}, "projects": []},
        review_queue={"items": []},
        task_queue={"tasks": []},
        round_state={"current_round": "round_43_test", "status": "in_progress", "next_round": "round_44"},
        dry_run_commands=["python3 scripts/agent_gate.py"],
    )
    assert "round_43_test" in text
    assert "OpenClaw" in text
