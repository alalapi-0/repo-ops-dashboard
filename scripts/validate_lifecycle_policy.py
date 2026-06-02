#!/usr/bin/env python3
"""Validate lifecycle_policy.yaml for Round 37 lifecycle rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_STATES = (
    "idea",
    "bootstrap",
    "active",
    "blocked",
    "maintenance",
    "frozen",
    "archived",
    "abandoned",
)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def read_lifecycle_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def validate_lifecycle_policy(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""

    if not str(data.get("schema_version", "")).strip():
        errors.append(f"{prefix}schema_version is required")
    if str(data.get("lifecycle_version", "")).strip() != "v1":
        errors.append(f"{prefix}lifecycle_version must be v1")

    states = data.get("states")
    if not isinstance(states, list):
        errors.append(f"{prefix}states must be a list")
    else:
        missing = [item for item in REQUIRED_STATES if item not in states]
        if missing:
            errors.append(f"{prefix}states missing: {missing}")

    rules = data.get("rules")
    if not isinstance(rules, dict):
        errors.append(f"{prefix}rules must be a mapping")
    else:
        maint = rules.get("low_health_maintenance")
        if not isinstance(maint, dict) or "threshold" not in maint:
            errors.append(f"{prefix}rules.low_health_maintenance requires threshold")

    return errors


def summarize_lifecycle_policy(data: dict[str, Any]) -> dict[str, Any]:
    states = data.get("states", [])
    return {
        "schema_version": str(data.get("schema_version", "")),
        "lifecycle_version": str(data.get("lifecycle_version", "")),
        "state_count": len(states) if isinstance(states, list) else 0,
        "states": [str(item) for item in states] if isinstance(states, list) else [],
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate lifecycle_policy.yaml")
    parser.add_argument("path", nargs="?", default="config/lifecycle_policy.yaml")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        data = read_lifecycle_policy(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}")
        return 1

    errors = validate_lifecycle_policy(data, path.name)
    if errors:
        for item in errors:
            print(f"[invalid] {item}")
        return 1

    summary = summarize_lifecycle_policy(data)
    print(
        f"[ok] lifecycle_policy valid: v={summary['lifecycle_version']} "
        f"states={summary['state_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
