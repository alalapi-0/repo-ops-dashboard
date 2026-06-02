#!/usr/bin/env python3
"""Validate blocker_policy.yaml for Round 38 blocker management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_TYPE_IDS = ("governance_missing", "repository_path", "repository_empty")
REQUIRED_ESCALATION_LEVELS = ("info", "warning", "review", "hitl")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def read_blocker_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def validate_blocker_policy(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""

    if not str(data.get("schema_version", "")).strip():
        errors.append(f"{prefix}schema_version is required")
    if str(data.get("blocker_version", "")).strip() != "v1":
        errors.append(f"{prefix}blocker_version must be v1")

    types = data.get("types")
    if not isinstance(types, list) or not types:
        errors.append(f"{prefix}types must be a non-empty list")
    else:
        seen: set[str] = set()
        for entry in types:
            if not isinstance(entry, dict):
                errors.append(f"{prefix}types entries must be mappings")
                continue
            type_id = str(entry.get("id", "")).strip()
            if not type_id:
                errors.append(f"{prefix}types entry missing id")
                continue
            seen.add(type_id)
            patterns = entry.get("patterns")
            if not isinstance(patterns, list) or not patterns:
                errors.append(f"{prefix}types.{type_id}.patterns must be a non-empty list")
        missing_types = [item for item in REQUIRED_TYPE_IDS if item not in seen]
        if missing_types:
            errors.append(f"{prefix}types missing ids: {missing_types}")

    escalation = data.get("escalation")
    if not isinstance(escalation, dict):
        errors.append(f"{prefix}escalation must be a mapping")
    else:
        levels = escalation.get("levels")
        if not isinstance(levels, list) or not levels:
            errors.append(f"{prefix}escalation.levels must be a non-empty list")
        else:
            seen_levels: set[str] = set()
            prev_days = -1
            for entry in levels:
                if not isinstance(entry, dict):
                    errors.append(f"{prefix}escalation.levels entries must be mappings")
                    continue
                level = str(entry.get("level", "")).strip()
                if not level:
                    errors.append(f"{prefix}escalation level missing level id")
                    continue
                seen_levels.add(level)
                if "after_days" not in entry:
                    errors.append(f"{prefix}escalation.{level}.after_days is required")
                else:
                    days = int(entry.get("after_days", -1))
                    if days < prev_days:
                        errors.append(f"{prefix}escalation levels must be ordered by after_days")
                    prev_days = days
                if not str(entry.get("action", "")).strip():
                    errors.append(f"{prefix}escalation.{level}.action is required")
            missing_levels = [item for item in REQUIRED_ESCALATION_LEVELS if item not in seen_levels]
            if missing_levels:
                errors.append(f"{prefix}escalation.levels missing: {missing_levels}")

    defaults = data.get("defaults")
    if not isinstance(defaults, dict):
        errors.append(f"{prefix}defaults must be a mapping")
    elif not str(defaults.get("unknown_type", "")).strip():
        errors.append(f"{prefix}defaults.unknown_type is required")

    return errors


def summarize_blocker_policy(data: dict[str, Any]) -> dict[str, Any]:
    types = data.get("types", [])
    levels = data.get("escalation", {}).get("levels", [])
    type_ids = [str(item.get("id", "")) for item in types if isinstance(item, dict)]
    level_ids = [str(item.get("level", "")) for item in levels if isinstance(item, dict)]
    return {
        "schema_version": str(data.get("schema_version", "")),
        "blocker_version": str(data.get("blocker_version", "")),
        "type_count": len(type_ids),
        "type_ids": type_ids,
        "escalation_levels": level_ids,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate blocker_policy.yaml")
    parser.add_argument("path", nargs="?", default="config/blocker_policy.yaml")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        data = read_blocker_policy(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}")
        return 1

    errors = validate_blocker_policy(data, path.name)
    if errors:
        for item in errors:
            print(f"[invalid] {item}")
        return 1

    summary = summarize_blocker_policy(data)
    print(
        f"[ok] blocker_policy valid: v={summary['blocker_version']} "
        f"types={summary['type_count']} escalation={len(summary['escalation_levels'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
