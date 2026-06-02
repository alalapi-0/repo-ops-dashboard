"""Tests for agent_run JSONL validation and manual recording."""

from __future__ import annotations

import json
from pathlib import Path

import validate_agent_run as var


def test_validate_example_run() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "governance" / "runs" / "example_run.jsonl"
    assert not var.validate_agent_run(path)


def test_validate_detects_unknown_event_type() -> None:
    event = var.build_event(
        event_type="not_a_real_event",
        timestamp="2026-06-02T00:00:00Z",
        task_id="task_x",
        project_id="repo_ops_dashboard",
        agent_type="Cursor",
        cwd="/tmp",
    )
    errors = var.validate_event(event)
    assert any("unknown event_type" in err for err in errors)


def test_read_example_run_has_run_started() -> None:
    root = Path(__file__).resolve().parents[1]
    events = var.read_agent_run(root / "governance" / "runs" / "example_run.jsonl")
    types = {event["event_type"] for event in events}
    assert "run_started" in types
    assert "task_completed" in types


def test_build_event_round_trip() -> None:
    event = var.build_event(
        event_type="run_started",
        timestamp="2026-06-02T00:00:00Z",
        task_id="task_round_30",
        project_id="repo_ops_dashboard",
        agent_type="Cursor",
        cwd="/tmp",
        payload={"round": "30"},
    )
    assert not var.validate_event(event)
    raw = json.dumps(event, ensure_ascii=False)
    loaded = var.load_json_line(raw)
    assert loaded["payload"]["round"] == "30"


def test_discover_run_files_includes_example() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = var.discover_run_files(root / "governance" / "runs")
    names = {p.name for p in paths}
    assert "example_run.jsonl" in names
