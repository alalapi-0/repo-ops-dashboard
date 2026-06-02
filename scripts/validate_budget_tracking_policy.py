#!/usr/bin/env python3
"""Validate config/budget_tracking_policy.yaml structure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_TOP = ("schema_version", "sources", "mock_rates", "estimation", "defaults")
REQUIRED_SOURCES = ("project_registry", "output", "report")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: root must be a mapping")
    return data


def validate_budget_tracking_policy(data: dict[str, Any], source: str = "") -> list[str]:
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

    rates = data.get("mock_rates", {})
    if not isinstance(rates, dict) or not rates.get("per_agent_run"):
        errors.append(f"{prefix}mock_rates.per_agent_run must be non-empty")

    defaults = data.get("defaults", {})
    if defaults.get("allow_external_billing_api") is True:
        errors.append(f"{prefix}allow_external_billing_api must remain false in governance rounds")
    return errors


def validate_budget_tracking_policy_file(path: Path) -> list[str]:
    return validate_budget_tracking_policy(load_yaml(path), source=path.name)


def main() -> int:
    root = Path(".").resolve()
    path = root / "config" / "budget_tracking_policy.yaml"
    errors = validate_budget_tracking_policy_file(path)
    if errors:
        for err in errors:
            print(f"[budget_tracking_policy] {err}")
        return 2
    print("[budget_tracking_policy] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
