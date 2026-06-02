#!/usr/bin/env python3
"""Validate agent_run JSONL audit trail files and individual events."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TEMPLATE_NAME = "agent_run_event.template.json"
REQUIRED_EVENT_FIELDS = (
    "event_type",
    "timestamp",
    "task_id",
    "project_id",
    "agent_type",
    "cwd",
    "payload",
    "error",
    "proof_of_work_path",
)
ALLOWED_EVENT_TYPES = frozenset(
    {
        "task_created",
        "task_assigned",
        "handoff_created",
        "run_started",
        "command_planned",
        "command_executed",
        "file_read",
        "file_written",
        "validation_started",
        "validation_finished",
        "blocker_detected",
        "review_requested",
        "proof_submitted",
        "task_completed",
        "task_failed",
    }
)


def load_json_line(line: str, source: str = "") -> dict[str, Any]:
    prefix = f"{source}: " if source else ""
    try:
        data = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{prefix}invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{prefix}event must be a JSON object")
    return data


def validate_event(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""
    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in data]
    if missing:
        errors.append(f"{prefix}missing fields: {missing}")
    event_type = str(data.get("event_type", "")).strip()
    if event_type and event_type not in ALLOWED_EVENT_TYPES:
        errors.append(f"{prefix}unknown event_type: {event_type}")
    task_id = str(data.get("task_id", "")).strip()
    if task_id and not task_id.startswith("task_"):
        errors.append(f"{prefix}task_id should start with task_")
    if "payload" in data and not isinstance(data.get("payload"), dict):
        errors.append(f"{prefix}payload must be an object")
    return errors


def read_agent_run(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            source = f"{path.name}:{line_no}"
            events.append(load_json_line(line, source))
    return events


def validate_agent_run(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        events = read_agent_run(path)
    except FileNotFoundError:
        return [f"{path.name}: file not found"]
    except ValueError as exc:
        return [str(exc)]
    if not events:
        errors.append(f"{path.name}: no events found")
    for line_no, event in enumerate(events, start=1):
        errors.extend(validate_event(event, f"{path.name}:{line_no}"))
    return errors


def discover_run_files(runs_dir: Path) -> list[Path]:
    if not runs_dir.is_dir():
        return []
    return sorted(p for p in runs_dir.glob("*.jsonl") if p.is_file())


def build_event(
    *,
    event_type: str,
    timestamp: str,
    task_id: str,
    project_id: str,
    agent_type: str,
    cwd: str,
    payload: dict[str, Any] | None = None,
    error: str | None = None,
    proof_of_work_path: str | None = None,
) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "timestamp": timestamp,
        "task_id": task_id,
        "project_id": project_id,
        "agent_type": agent_type,
        "cwd": cwd,
        "payload": payload or {},
        "error": error,
        "proof_of_work_path": proof_of_work_path,
    }
