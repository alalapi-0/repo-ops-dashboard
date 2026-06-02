#!/usr/bin/env python3
"""Validate ui_check_policy.yaml for Round 40 Playwright dashboard validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_CHECKS = (
    "page_title",
    "dashboard_container",
    "governance_v2_section",
    "gov_panel_portfolio_state",
    "gov_panel_task_queue",
    "gov_panel_review_queue",
    "gov_panel_blockers",
    "screenshot",
    "console_no_errors",
    "network_no_failed_requests",
)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def read_ui_check_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def validate_ui_check_policy(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""

    if not str(data.get("schema_version", "")).strip():
        errors.append(f"{prefix}schema_version is required")
    if str(data.get("ui_check_version", "")).strip() != "v1":
        errors.append(f"{prefix}ui_check_version must be v1")

    access = data.get("access")
    if not isinstance(access, dict):
        errors.append(f"{prefix}access must be a mapping")
    else:
        schemes = access.get("allowed_schemes")
        if not isinstance(schemes, list) or "file" not in schemes:
            errors.append(f"{prefix}access.allowed_schemes must include file")

    checks = data.get("required_checks")
    if not isinstance(checks, list) or not checks:
        errors.append(f"{prefix}required_checks must be a non-empty list")
    else:
        missing = [item for item in REQUIRED_CHECKS if item not in checks]
        if missing:
            errors.append(f"{prefix}required_checks missing: {missing}")

    interactions = data.get("interaction_checks")
    if not isinstance(interactions, list) or not interactions:
        errors.append(f"{prefix}interaction_checks must be a non-empty list")

    return errors


def summarize_ui_check_policy(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "ui_check_version": data.get("ui_check_version"),
        "required_check_count": len(data.get("required_checks") or []),
        "interaction_check_count": len(data.get("interaction_checks") or []),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    live = root / "config" / "ui_check_policy.yaml"
    data = read_ui_check_policy(live)
    errors = validate_ui_check_policy(data, live.name)
    if errors:
        for err in errors:
            print(f"[error] {err}")
        return 1
    summary = summarize_ui_check_policy(data)
    print(
        "[ok] ui_check_policy valid "
        f"({summary.get('required_check_count')} required, "
        f"{summary.get('interaction_check_count')} interaction)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
