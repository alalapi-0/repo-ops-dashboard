#!/usr/bin/env python3
"""Classify blockers and compute timeout escalation levels."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_blocker_policy(path: Path | None = None) -> dict[str, Any]:
    policy_path = path or Path("config/blocker_policy.yaml")
    return load_yaml(policy_path)


def classify_blocker(text: str, policy: dict[str, Any]) -> str:
    message = str(text).strip()
    defaults = dict(policy.get("defaults", {}))
    fallback = str(defaults.get("unknown_type", "governance_missing"))

    for entry in policy.get("types", []):
        if not isinstance(entry, dict):
            continue
        type_id = str(entry.get("id", "")).strip()
        for pattern in entry.get("patterns", []):
            if str(pattern) in message:
                return type_id
    return fallback


def compute_escalation_level(age_days: int, policy: dict[str, Any]) -> dict[str, Any]:
    levels = list(policy.get("escalation", {}).get("levels", []))
    chosen = levels[0] if levels else {"level": "info", "after_days": 0, "action": "log_only"}
    for entry in levels:
        if not isinstance(entry, dict):
            continue
        if age_days >= int(entry.get("after_days", 0)):
            chosen = entry
    return {
        "level": str(chosen.get("level", "info")),
        "action": str(chosen.get("action", "log_only")),
        "after_days": int(chosen.get("after_days", 0)),
    }


def enrich_blockers(
    blockers: list[str],
    *,
    age_days: int = 0,
    policy: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    cfg = policy or load_blocker_policy()
    defaults = dict(cfg.get("defaults", {}))
    fallback_owner = str(defaults.get("fallback_owner", "Human"))
    type_index = {
        str(entry.get("id", "")): entry
        for entry in cfg.get("types", [])
        if isinstance(entry, dict) and entry.get("id")
    }

    enriched: list[dict[str, Any]] = []
    for text in blockers:
        type_id = classify_blocker(text, cfg)
        type_meta = dict(type_index.get(type_id, {}))
        escalation = compute_escalation_level(age_days, cfg)
        enriched.append(
            {
                "message": str(text),
                "type": type_id,
                "severity": str(type_meta.get("severity", "medium")),
                "owner": str(type_meta.get("default_owner", fallback_owner)),
                "age_days": age_days,
                "escalation_level": escalation["level"],
                "escalation_action": escalation["action"],
            }
        )
    return enriched


def summarize_blockers(blockers: list[str], *, age_days: int = 0, policy: dict[str, Any] | None = None) -> dict[str, Any]:
    details = enrich_blockers(blockers, age_days=age_days, policy=policy)
    if not details:
        return {"count": 0, "max_escalation": "none", "types": []}
    levels = {"info": 0, "warning": 1, "review": 2, "hitl": 3}
    max_level = max(details, key=lambda item: levels.get(str(item.get("escalation_level", "info")), 0))
    return {
        "count": len(details),
        "max_escalation": str(max_level.get("escalation_level", "info")),
        "types": sorted({str(item.get("type", "")) for item in details}),
        "details": details,
    }
