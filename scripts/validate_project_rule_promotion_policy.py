#!/usr/bin/env python3
"""Validate config/project_rule_promotion_policy.yaml structure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_TOP = ("schema_version", "sources", "selection", "promotion", "defaults")
REQUIRED_SOURCES = ("playbook_candidates", "proposal_output", "review_queue_ref", "report")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: root must be a mapping")
    return data


def validate_project_rule_promotion_policy(data: dict[str, Any], source: str = "") -> list[str]:
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

    promotion = data.get("promotion", {})
    if not isinstance(promotion, dict) or not promotion.get("review_type"):
        errors.append(f"{prefix}promotion.review_type required")
    return errors


def validate_project_rule_promotion_policy_file(path: Path) -> list[str]:
    return validate_project_rule_promotion_policy(load_yaml(path), source=path.name)


def main() -> int:
    root = Path(".").resolve()
    path = root / "config" / "project_rule_promotion_policy.yaml"
    errors = validate_project_rule_promotion_policy_file(path)
    if errors:
        for err in errors:
            print(f"[project_rule_promotion_policy] {err}")
        return 2
    print("[project_rule_promotion_policy] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
