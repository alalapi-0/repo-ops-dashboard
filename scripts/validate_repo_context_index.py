#!/usr/bin/env python3
"""Validate repo_context_index.yaml structure and safety boundaries."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_FIELDS = (
    "project_id",
    "repo_name",
    "summary",
    "domain",
    "current_stage",
    "key_files",
    "key_commands",
    "roadmap_summary",
    "known_blockers",
    "last_change_summary",
    "next_actions",
    "updated_at",
)

LIST_FIELDS = ("key_files", "key_commands", "known_blockers", "next_actions")
SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|secret|token|password|private[_-]?key)")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: root must be a mapping")
    return data


def read_repo_context_index(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def validate_repo_context_index(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        errors.append(f"{prefix}missing fields: {missing}")
    for field in LIST_FIELDS:
        value = data.get(field)
        if value is not None and not isinstance(value, list):
            errors.append(f"{prefix}{field} must be a list")
    summary = str(data.get("summary", ""))
    if summary and len(summary) > 500:
        errors.append(f"{prefix}summary too long (>500 chars)")
    for field in ("summary", "roadmap_summary", "last_change_summary"):
        text = str(data.get(field, ""))
        if SECRET_PATTERN.search(text):
            errors.append(f"{prefix}{field} contains suspicious secret-like token")
    updated_at = str(data.get("updated_at", "")).strip()
    if updated_at:
        try:
            datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{prefix}updated_at must be ISO-8601")
    return errors


def summarize_repo_context_index(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": data.get("project_id"),
        "repo_name": data.get("repo_name"),
        "current_stage": data.get("current_stage"),
        "key_files_count": len(data.get("key_files") or []),
        "key_commands_count": len(data.get("key_commands") or []),
        "known_blockers_count": len(data.get("known_blockers") or []),
        "next_actions_count": len(data.get("next_actions") or []),
    }


def build_repo_context_index_stub(
    *,
    project_id: str,
    repo_name: str,
    domain: str,
    current_stage: str,
    summary: str,
    key_files: list[str] | None = None,
    key_commands: list[str] | None = None,
    roadmap_summary: str = "",
    known_blockers: list[str] | None = None,
    next_actions: list[str] | None = None,
    last_change_summary: str = "Initial repo_context_index stub.",
) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "project_id": project_id,
        "repo_name": repo_name,
        "summary": summary,
        "domain": domain,
        "current_stage": current_stage,
        "key_files": key_files or ["README.md", "AGENTS.md", "repo_context_index.yaml"],
        "key_commands": key_commands or ["python3 scripts/agent_gate.py"],
        "roadmap_summary": roadmap_summary or "See docs/roadmap_40_rounds.md.",
        "known_blockers": known_blockers or [],
        "last_change_summary": last_change_summary,
        "next_actions": next_actions or ["Keep repo_context_index.yaml updated after major changes."],
        "updated_at": datetime.now().astimezone().replace(microsecond=0).isoformat(),
    }
