#!/usr/bin/env python3
"""Validate proof_of_work JSON documents against the governance template."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TEMPLATE_NAME = "proof_of_work.template.json"
REQUIRED_POW_FIELDS = (
    "task_id",
    "project_id",
    "status",
    "completed_at",
    "agent_type",
    "working_directory",
    "artifacts",
    "changed_files",
    "validation_commands",
    "tests_passed",
    "audit_run_path",
    "summary",
    "known_issues",
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: root must be a JSON object")
    return data


def discover_proof_files(pow_dir: Path) -> list[Path]:
    if not pow_dir.is_dir():
        return []
    paths = sorted(pow_dir.glob("*.json"))
    return [p for p in paths if p.name != TEMPLATE_NAME]


def validate_proof_of_work(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""
    missing = [field for field in REQUIRED_POW_FIELDS if field not in data]
    if missing:
        errors.append(f"{prefix}missing fields: {missing}")
    task_id = str(data.get("task_id", "")).strip()
    if task_id and not task_id.startswith("task_"):
        errors.append(f"{prefix}task_id should start with task_")
    if "tests_passed" in data and not isinstance(data.get("tests_passed"), bool):
        errors.append(f"{prefix}tests_passed must be boolean")
    for key in ("artifacts", "changed_files", "validation_commands", "known_issues"):
        if key in data and not isinstance(data.get(key), list):
            errors.append(f"{prefix}{key} must be a list")
    return errors


def read_proof_of_work(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_json(path)
