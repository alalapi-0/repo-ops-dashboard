#!/usr/bin/env python3
"""Validate scan_policy.yaml structure and core governance categories."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_CORE_CATEGORIES = ("readme", "agents", "protocol", "round_state")
REQUIRED_SAFETY_KEYS = ("default_dry_run", "max_file_kb", "deny_env_files")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def read_scan_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def validate_scan_policy(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""

    if not str(data.get("schema_version", "")).strip():
        errors.append(f"{prefix}schema_version is required")
    if str(data.get("scanner_version", "")).strip() != "v2":
        errors.append(f"{prefix}scanner_version must be v2")

    core = data.get("core_governance")
    if not isinstance(core, dict):
        errors.append(f"{prefix}core_governance must be a mapping")
        return errors

    for category in REQUIRED_CORE_CATEGORIES:
        entry = core.get(category)
        if not isinstance(entry, dict):
            errors.append(f"{prefix}core_governance.{category} missing or invalid")
            continue
        patterns = entry.get("patterns")
        if not isinstance(patterns, list) or not patterns:
            errors.append(f"{prefix}core_governance.{category}.patterns must be a non-empty list")
        if "required" not in entry:
            errors.append(f"{prefix}core_governance.{category}.required must be set")

    safety = data.get("safety")
    if not isinstance(safety, dict):
        errors.append(f"{prefix}safety must be a mapping")
    else:
        for key in REQUIRED_SAFETY_KEYS:
            if key not in safety:
                errors.append(f"{prefix}safety.{key} is required")

    return errors


def summarize_scan_policy(data: dict[str, Any]) -> dict[str, Any]:
    core = data.get("core_governance", {})
    categories: list[str] = []
    required_categories: list[str] = []
    pattern_count = 0
    if isinstance(core, dict):
        for name, entry in core.items():
            if not isinstance(entry, dict):
                continue
            categories.append(str(name))
            if entry.get("required"):
                required_categories.append(str(name))
            patterns = entry.get("patterns", [])
            if isinstance(patterns, list):
                pattern_count += len(patterns)
    safety = data.get("safety", {})
    return {
        "schema_version": str(data.get("schema_version", "")),
        "scanner_version": str(data.get("scanner_version", "")),
        "core_categories": categories,
        "required_categories": required_categories,
        "pattern_count": pattern_count,
        "default_dry_run": bool(safety.get("default_dry_run", True)) if isinstance(safety, dict) else True,
        "max_file_kb": int(safety.get("max_file_kb", 512)) if isinstance(safety, dict) else 512,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate scan_policy.yaml")
    parser.add_argument("path", nargs="?", default="config/scan_policy.yaml")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        data = read_scan_policy(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}")
        return 1

    errors = validate_scan_policy(data, path.name)
    if errors:
        for item in errors:
            print(f"[invalid] {item}")
        return 1

    summary = summarize_scan_policy(data)
    print(
        f"[ok] scan_policy valid: v={summary['scanner_version']} "
        f"categories={len(summary['core_categories'])} patterns={summary['pattern_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
