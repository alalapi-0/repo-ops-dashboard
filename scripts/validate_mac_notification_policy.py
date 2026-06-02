#!/usr/bin/env python3
"""Validate config/mac_notification_policy.yaml structure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_TOP = ("schema_version", "sources", "content", "delivery", "defaults")
REQUIRED_SOURCES = ("daily_brief", "repo_status", "output_payload")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: root must be a mapping")
    return data


def validate_mac_notification_policy(data: dict[str, Any], source: str = "") -> list[str]:
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

    defaults = data.get("defaults", {})
    if isinstance(defaults, dict) and defaults.get("external_api") is True:
        errors.append(f"{prefix}defaults.external_api must be false")

    return errors


def validate_mac_notification_policy_file(path: Path) -> list[str]:
    return validate_mac_notification_policy(load_yaml(path), source=path.name)


def main() -> int:
    root = Path(".").resolve()
    path = root / "config" / "mac_notification_policy.yaml"
    errors = validate_mac_notification_policy_file(path)
    if errors:
        for err in errors:
            print(f"[mac_notification_policy] {err}")
        return 2
    print("[mac_notification_policy] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
