#!/usr/bin/env python3
"""Validate priority_scoring_policy.yaml for Round 36 scoring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_FACTORS = ("impact", "urgency", "unblock", "cost", "risk")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def read_priority_scoring_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def validate_priority_scoring_policy(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""

    if not str(data.get("schema_version", "")).strip():
        errors.append(f"{prefix}schema_version is required")
    if str(data.get("scoring_version", "")).strip() != "v1":
        errors.append(f"{prefix}scoring_version must be v1")

    formula = data.get("formula")
    if not isinstance(formula, dict):
        errors.append(f"{prefix}formula must be a mapping")
    elif not int(formula.get("product_scale", 0)):
        errors.append(f"{prefix}formula.product_scale must be positive")

    factors = data.get("factors")
    if not isinstance(factors, dict):
        errors.append(f"{prefix}factors must be a mapping")
    else:
        for name in REQUIRED_FACTORS:
            entry = factors.get(name)
            if not isinstance(entry, dict):
                errors.append(f"{prefix}factors.{name} missing or invalid")
                continue
            if "max" not in entry:
                errors.append(f"{prefix}factors.{name}.max is required")

    bands = data.get("priority_bands")
    if not isinstance(bands, dict):
        errors.append(f"{prefix}priority_bands must be a mapping")
    else:
        for key in ("high", "medium"):
            if key not in bands:
                errors.append(f"{prefix}priority_bands.{key} is required")

    return errors


def summarize_priority_scoring_policy(data: dict[str, Any]) -> dict[str, Any]:
    factors = data.get("factors", {})
    factor_names = list(factors.keys()) if isinstance(factors, dict) else []
    formula = data.get("formula", {})
    return {
        "schema_version": str(data.get("schema_version", "")),
        "scoring_version": str(data.get("scoring_version", "")),
        "factors": factor_names,
        "product_scale": int(formula.get("product_scale", 0)) if isinstance(formula, dict) else 0,
        "expression": str(formula.get("expression", "")) if isinstance(formula, dict) else "",
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate priority_scoring_policy.yaml")
    parser.add_argument("path", nargs="?", default="config/priority_scoring_policy.yaml")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        data = read_priority_scoring_policy(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}")
        return 1

    errors = validate_priority_scoring_policy(data, path.name)
    if errors:
        for item in errors:
            print(f"[invalid] {item}")
        return 1

    summary = summarize_priority_scoring_policy(data)
    print(
        f"[ok] priority_scoring_policy valid: v={summary['scoring_version']} "
        f"factors={len(summary['factors'])} scale={summary['product_scale']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
