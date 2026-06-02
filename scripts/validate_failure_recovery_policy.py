#!/usr/bin/env python3
"""Validate config/failure_recovery_policy.yaml structure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_TOP = ("schema_version", "retry", "failure_classes", "checkpoint", "review_queue_escalation")
REQUIRED_RETRY = ("max_retry_count", "backoff_hours")
REQUIRED_CHECKPOINT = ("id_prefix", "required_on_failure", "snapshot_dir")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: root must be a mapping")
    return data


def validate_failure_recovery_policy(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""
    missing = [key for key in REQUIRED_TOP if key not in data]
    if missing:
        errors.append(f"{prefix}missing top-level keys: {missing}")

    retry = data.get("retry", {})
    if isinstance(retry, dict):
        missing_retry = [k for k in REQUIRED_RETRY if k not in retry]
        if missing_retry:
            errors.append(f"{prefix}retry missing: {missing_retry}")
        max_count = int(retry.get("max_retry_count", 0))
        backoff = retry.get("backoff_hours", [])
        if max_count < 1:
            errors.append(f"{prefix}max_retry_count must be >= 1")
        if not isinstance(backoff, list) or len(backoff) < 1:
            errors.append(f"{prefix}backoff_hours must be a non-empty list")
    else:
        errors.append(f"{prefix}retry must be a mapping")

    classes = data.get("failure_classes", [])
    if not isinstance(classes, list) or not classes:
        errors.append(f"{prefix}failure_classes must be a non-empty list")
    else:
        ids = set()
        for entry in classes:
            if not isinstance(entry, dict):
                errors.append(f"{prefix}failure_class entry must be mapping")
                continue
            class_id = str(entry.get("id", "")).strip()
            if not class_id:
                errors.append(f"{prefix}failure_class missing id")
            elif class_id in ids:
                errors.append(f"{prefix}duplicate failure_class id: {class_id}")
            else:
                ids.add(class_id)

    checkpoint = data.get("checkpoint", {})
    if isinstance(checkpoint, dict):
        missing_ck = [k for k in REQUIRED_CHECKPOINT if k not in checkpoint]
        if missing_ck:
            errors.append(f"{prefix}checkpoint missing: {missing_ck}")
    else:
        errors.append(f"{prefix}checkpoint must be a mapping")

    escalation = data.get("review_queue_escalation", {})
    levels = escalation.get("levels", []) if isinstance(escalation, dict) else []
    if not levels:
        errors.append(f"{prefix}review_queue_escalation.levels empty")
    return errors


def validate_failure_recovery_policy_file(path: Path) -> list[str]:
    return validate_failure_recovery_policy(load_yaml(path), source=path.name)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate failure_recovery_policy.yaml")
    parser.add_argument("--path", default="config/failure_recovery_policy.yaml")
    args = parser.parse_args()
    path = Path(args.path)
    errors = validate_failure_recovery_policy_file(path)
    if errors:
        for err in errors:
            print(f"[failure_recovery] {err}")
        return 2
    print(f"[failure_recovery] valid: {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
