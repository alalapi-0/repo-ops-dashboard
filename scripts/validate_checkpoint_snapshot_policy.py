#!/usr/bin/env python3
"""Validate config/checkpoint_snapshot_policy.yaml structure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_TOP = ("schema_version", "snapshot", "defaults")
REQUIRED_SNAPSHOT = ("source", "output_dir", "manifest", "id_prefix", "max_retained")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: root must be a mapping")
    return data


def validate_checkpoint_snapshot_policy(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""
    missing = [key for key in REQUIRED_TOP if key not in data]
    if missing:
        errors.append(f"{prefix}missing top-level keys: {missing}")

    snap = data.get("snapshot", {})
    if isinstance(snap, dict):
        missing_snap = [k for k in REQUIRED_SNAPSHOT if k not in snap]
        if missing_snap:
            errors.append(f"{prefix}snapshot missing: {missing_snap}")
        max_retained = int(snap.get("max_retained", 0))
        if max_retained < 1:
            errors.append(f"{prefix}max_retained must be >= 1")
        id_prefix = str(snap.get("id_prefix", "")).strip()
        if not id_prefix:
            errors.append(f"{prefix}id_prefix must be non-empty")
    else:
        errors.append(f"{prefix}snapshot must be a mapping")

    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        errors.append(f"{prefix}defaults must be a mapping")
    return errors


def validate_checkpoint_snapshot_policy_file(path: Path) -> list[str]:
    return validate_checkpoint_snapshot_policy(load_yaml(path), source=path.name)


def main() -> int:
    root = Path(".").resolve()
    path = root / "config" / "checkpoint_snapshot_policy.yaml"
    errors = validate_checkpoint_snapshot_policy_file(path)
    if errors:
        for err in errors:
            print(f"[checkpoint_snapshot_policy] {err}")
        return 2
    print("[checkpoint_snapshot_policy] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
