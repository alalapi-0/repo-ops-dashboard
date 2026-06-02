#!/usr/bin/env python3
"""Validate handoff_packet YAML against governance template and protocol rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_FIELDS = (
    "handoff_id",
    "parent_task_id",
    "target_agent",
    "working_directory",
    "task_spec_path",
    "context_refs",
    "allowed_files",
    "denied_files",
    "confirmation_policy",
    "execpolicy_profile",
    "expected_artifacts",
    "timeout",
    "return_contract",
)

ALLOWED_AGENTS = frozenset({"Cursor", "Codex", "OpenClaw", "HumanOwner"})


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: root must be a mapping")
    return data


def read_handoff_packet(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def validate_handoff_packet(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        errors.append(f"{prefix}missing fields: {missing}")

    handoff_id = str(data.get("handoff_id", "")).strip()
    if handoff_id and not handoff_id.startswith("handoff_"):
        errors.append(f"{prefix}handoff_id should start with handoff_")

    agent = str(data.get("target_agent", "")).strip()
    if agent and agent not in ALLOWED_AGENTS:
        errors.append(f"{prefix}unknown target_agent: {agent}")

    wd = str(data.get("working_directory", "")).strip()
    if not wd:
        errors.append(f"{prefix}working_directory is required")

    context_refs = data.get("context_refs")
    if context_refs is not None and not isinstance(context_refs, list):
        errors.append(f"{prefix}context_refs must be a list")

    contract = data.get("return_contract")
    if isinstance(contract, dict):
        if not contract.get("validation_commands"):
            errors.append(f"{prefix}return_contract.validation_commands required")
    elif contract is not None:
        errors.append(f"{prefix}return_contract must be a mapping")

    denied = data.get("denied_files")
    if isinstance(denied, list):
        joined = " ".join(str(item) for item in denied).lower()
        if ".env" not in joined:
            errors.append(f"{prefix}denied_files should include .env patterns")

    return errors


def validate_handoff_file(path: Path) -> list[str]:
    return validate_handoff_packet(read_handoff_packet(path), source=path.name)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate a handoff_packet YAML file")
    parser.add_argument("path", help="Path to handoff_packet YAML")
    args = parser.parse_args()
    path = Path(args.path)
    errors = validate_handoff_file(path)
    if errors:
        for err in errors:
            print(f"[handoff] {err}")
        return 2
    print(f"[handoff] valid: {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
