"""Tests for generate_dashboard governance v2 panels."""

from __future__ import annotations

from pathlib import Path

import generate_dashboard as gd

ROOT = Path(__file__).resolve().parents[1]


def test_render_governance_v2_includes_panels() -> None:
    portfolio = {
        "generated_at": "2026-06-02T00:00:00Z",
        "summary": {"total_projects": 1, "active_projects": 1, "blocked_projects": 0, "review_queue_open": 1},
        "projects": [{"project_id": "demo", "lifecycle": "active", "priority": "high", "blockers": []}],
    }
    task_queue = {
        "generated_at": "2026-06-02T00:00:00Z",
        "summary": {"total_tasks": 1, "active_tasks": 1},
        "tasks": [{"task_id": "t1", "project_id": "demo", "status": "proposed", "assigned_agent": "Cursor"}],
    }
    review_queue = {
        "updated_at": "2026-06-02T00:00:00Z",
        "items": [{"review_id": "rq1", "type": "test", "project_id": "demo", "status": "open"}],
    }
    repos = [
        {
            "name": "blocked-repo",
            "blockers": ["AGENTS.md missing"],
            "blocker_details": [
                {
                    "type": "governance_missing",
                    "owner": "Cursor",
                    "escalation_level": "info",
                }
            ],
            "blocker_max_escalation": "info",
        }
    ]
    html = gd.render_governance_v2(portfolio, task_queue, review_queue, repos)
    assert 'data-dashboard-v2-ready="true"' in html
    assert 'data-panel="portfolio_state"' in html
    assert 'data-panel="task_queue"' in html
    assert 'data-panel="review_queue"' in html
    assert 'data-panel="blockers"' in html
    assert "blocked-repo" in html


def test_main_generates_dashboard_with_v2(tmp_path: Path) -> None:
    status = {
        "generated_at": "2026-06-02T00:00:00Z",
        "repos": [{"name": "demo", "type": "meta_ops", "status": "active", "priority": "high", "blockers": []}],
    }
    status_path = tmp_path / "status.json"
    status_path.write_text(__import__("json").dumps(status), encoding="utf-8")
    out_path = tmp_path / "index.html"

    import sys
    from unittest.mock import patch

    argv = [
        "generate_dashboard.py",
        "--input",
        str(status_path),
        "--output",
        str(out_path),
        "--portfolio-state",
        str(ROOT / "governance" / "portfolio_state.example.yaml"),
        "--task-queue",
        str(ROOT / "governance" / "governance_task_queue.example.yaml"),
        "--review-queue",
        str(ROOT / "governance" / "review_queue.example.yaml"),
        "--human-notes",
        str(ROOT / "data" / "human_notes.example.json"),
    ]
    with patch.object(sys, "argv", argv):
        assert gd.main() == 0

    text = out_path.read_text(encoding="utf-8")
    assert "data-dashboard-v2-ready" in text
    assert "治理面板 V2" in text
