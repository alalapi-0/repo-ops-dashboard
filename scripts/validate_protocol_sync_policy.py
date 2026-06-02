#!/usr/bin/env python3
"""Validate config/protocol_sync_policy.yaml structure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_TOP = ("schema_version", "sources", "governance_files", "priority_rules", "defaults")
REQUIRED_SOURCES = ("snapshots", "reference_protocol", "markdown_report", "yaml_output")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: root must be a mapping")
    return data


def validate_protocol_sync_policy(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""
    missing = [key for key in REQUIRED_TOP if key not in data]
    if missing:
        errors.append(f"{prefix}missing top-level keys: {missing}")

    sources = data.get("sources", {})
    if isinstance(sources, dict):
        missing_src = [k for k in REQUIRED_SOURCES if k not in sources]
        if missing_src:
            errors.append(f"{prefix}sources missing: {missing_src}")
    else:
        errors.append(f"{prefix}sources must be a mapping")

    files = data.get("governance_files", [])
    if not isinstance(files, list) or not files:
        errors.append(f"{prefix}governance_files must be a non-empty list")

    rules = data.get("priority_rules", {})
    if not isinstance(rules, dict) or not rules.get("high_missing"):
        errors.append(f"{prefix}priority_rules.high_missing must be non-empty")
    return errors


def validate_protocol_sync_policy_file(path: Path) -> list[str]:
    return validate_protocol_sync_policy(load_yaml(path), source=path.name)


def main() -> int:
    root = Path(".").resolve()
    path = root / "config" / "protocol_sync_policy.yaml"
    errors = validate_protocol_sync_policy_file(path)
    if errors:
        for err in errors:
            print(f"[protocol_sync_policy] {err}")
        return 2
    print("[protocol_sync_policy] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
