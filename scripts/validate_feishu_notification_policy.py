#!/usr/bin/env python3
"""Validate config/feishu_notification_policy.yaml structure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_TOP = ("schema_version", "sources", "channels", "schedule", "content_rules", "defaults")
REQUIRED_SOURCES = ("daily_report", "weekly_report", "output_plan", "output_report")
REQUIRED_SCHEDULE = ("daily", "weekly")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: root must be a mapping")
    return data


def validate_feishu_notification_policy(data: dict[str, Any], source: str = "") -> list[str]:
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

    schedule = data.get("schedule", {})
    if isinstance(schedule, dict):
        missing_sched = [k for k in REQUIRED_SCHEDULE if k not in schedule]
        if missing_sched:
            errors.append(f"{prefix}schedule missing: {missing_sched}")
    else:
        errors.append(f"{prefix}schedule must be a mapping")

    defaults = data.get("defaults", {})
    if isinstance(defaults, dict) and defaults.get("external_api") is True:
        errors.append(f"{prefix}defaults.external_api must be false for planning policy")

    return errors


def validate_feishu_notification_policy_file(path: Path) -> list[str]:
    return validate_feishu_notification_policy(load_yaml(path), source=path.name)


def main() -> int:
    root = Path(".").resolve()
    path = root / "config" / "feishu_notification_policy.yaml"
    errors = validate_feishu_notification_policy_file(path)
    if errors:
        for err in errors:
            print(f"[feishu_notification_policy] {err}")
        return 2
    print("[feishu_notification_policy] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
