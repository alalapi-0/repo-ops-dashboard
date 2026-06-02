#!/usr/bin/env python3
"""Validate analyzer_policy.yaml structure for status analyzer v2."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_DIMENSIONS = ("governance_files", "registry_alignment", "round_progress")
REQUIRED_ROUND_STATE_FIELDS = ("current_round", "status", "next_round")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def read_analyzer_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def validate_analyzer_policy(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""

    if not str(data.get("schema_version", "")).strip():
        errors.append(f"{prefix}schema_version is required")
    if str(data.get("analyzer_version", "")).strip() != "v2":
        errors.append(f"{prefix}analyzer_version must be v2")

    inputs = data.get("inputs")
    if not isinstance(inputs, dict):
        errors.append(f"{prefix}inputs must be a mapping")
    else:
        for key in ("registry", "round_state_file"):
            if not str(inputs.get(key, "")).strip():
                errors.append(f"{prefix}inputs.{key} is required")

    dimensions = data.get("health_dimensions")
    if not isinstance(dimensions, dict):
        errors.append(f"{prefix}health_dimensions must be a mapping")
    else:
        for name in REQUIRED_DIMENSIONS:
            entry = dimensions.get(name)
            if not isinstance(entry, dict):
                errors.append(f"{prefix}health_dimensions.{name} missing or invalid")
                continue
            if "weight" not in entry or "source" not in entry:
                errors.append(f"{prefix}health_dimensions.{name} requires weight and source")

    match_cfg = data.get("registry_match")
    if not isinstance(match_cfg, dict):
        errors.append(f"{prefix}registry_match must be a mapping")

    fields = data.get("round_state_fields")
    if not isinstance(fields, list):
        errors.append(f"{prefix}round_state_fields must be a list")
    else:
        missing = [item for item in REQUIRED_ROUND_STATE_FIELDS if item not in fields]
        if missing:
            errors.append(f"{prefix}round_state_fields missing: {missing}")

    return errors


def summarize_analyzer_policy(data: dict[str, Any]) -> dict[str, Any]:
    dimensions = data.get("health_dimensions", {})
    dim_names: list[str] = []
    total_weight = 0
    if isinstance(dimensions, dict):
        for name, entry in dimensions.items():
            if not isinstance(entry, dict):
                continue
            dim_names.append(str(name))
            total_weight += int(entry.get("weight", 0))
    inputs = data.get("inputs", {})
    return {
        "schema_version": str(data.get("schema_version", "")),
        "analyzer_version": str(data.get("analyzer_version", "")),
        "dimensions": dim_names,
        "total_weight": total_weight,
        "registry_path": str(inputs.get("registry", "")) if isinstance(inputs, dict) else "",
        "round_state_file": str(inputs.get("round_state_file", "")) if isinstance(inputs, dict) else "",
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate analyzer_policy.yaml")
    parser.add_argument("path", nargs="?", default="config/analyzer_policy.yaml")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        data = read_analyzer_policy(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}")
        return 1

    errors = validate_analyzer_policy(data, path.name)
    if errors:
        for item in errors:
            print(f"[invalid] {item}")
        return 1

    summary = summarize_analyzer_policy(data)
    print(
        f"[ok] analyzer_policy valid: v={summary['analyzer_version']} "
        f"dimensions={len(summary['dimensions'])} weight={summary['total_weight']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
