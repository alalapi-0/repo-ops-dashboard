"""Tests for run_handoff_trial (dry-run, no subprocess)."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_handoff_trial as trial  # noqa: E402


def test_build_pow_draft_has_trial_mode() -> None:
    draft = trial.build_pow_draft(
        task_spec={
            "task_id": "task_handoff_trial_001",
            "project_id": "repo_ops_dashboard",
            "working_directory": "/tmp/repo-ops-dashboard",
            "artifacts_expected": ["reports/handoff_trial_report.md"],
            "validation_commands": ["python3 scripts/agent_gate.py"],
        },
        handoff_id="handoff_handoff_trial_001",
        cursor_prompt_path="prompts/generated/task_handoff_trial_001_cursor.md",
    )
    assert draft["trial_mode"] is True
    assert draft["status"] == "draft"
    assert draft["external_api_called"] is False


def test_render_report_includes_handoff_id() -> None:
    text = trial.render_report(
        round_state={"current_round": "round_60", "status": "in_progress"},
        snapshot={"role": "openclaw_daily_briefing_skill", "repo_count": 5},
        handoff_id="handoff_handoff_trial_001",
        cursor_prompt_chars=1200,
        pow_draft={"status": "draft", "trial_mode": True},
        dry_run=True,
    )
    assert "handoff_handoff_trial_001" in text
    assert "dry_run=True" in text
