#!/usr/bin/env python3
"""Validate governance/review_queue.yaml structure and HITL decision rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_QUEUE_FIELDS = ("schema_version", "policy", "items")
REQUIRED_ITEM_FIELDS = (
    "review_id",
    "type",
    "project_id",
    "task_id",
    "prompt",
    "options",
    "context_refs",
    "status",
    "decision",
    "decided_at",
    "expires_at",
)
OPEN_STATUSES = frozenset({"open", "pending", "awaiting_human"})
CLOSED_STATUSES = frozenset({"decided", "expired", "cancelled"})


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: root must be a mapping")
    return data


def read_review_queue(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def validate_item(item: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""
    if not isinstance(item, dict):
        return [f"{prefix}item must be a mapping"]
    missing = [field for field in REQUIRED_ITEM_FIELDS if field not in item]
    if missing:
        errors.append(f"{prefix}missing fields: {missing}")
    review_id = str(item.get("review_id", "")).strip()
    if review_id and not review_id.startswith("rq_"):
        errors.append(f"{prefix}review_id should start with rq_")
    options = item.get("options")
    if options is not None and not isinstance(options, list):
        errors.append(f"{prefix}options must be a list")
    context_refs = item.get("context_refs")
    if context_refs is not None and not isinstance(context_refs, list):
        errors.append(f"{prefix}context_refs must be a list")
    status = str(item.get("status", "")).lower()
    decision = item.get("decision")
    decided_at = item.get("decided_at")
    if status in OPEN_STATUSES:
        if decision is not None:
            errors.append(f"{prefix}open item must have decision=null")
        if decided_at is not None:
            errors.append(f"{prefix}open item must have decided_at=null")
    elif status == "decided":
        if not decision:
            errors.append(f"{prefix}decided item requires decision")
        if not decided_at:
            errors.append(f"{prefix}decided item requires decided_at")
    elif status and status not in CLOSED_STATUSES:
        errors.append(f"{prefix}unknown status: {status}")
    return errors


def validate_review_queue(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""
    missing = [field for field in REQUIRED_QUEUE_FIELDS if field not in data]
    if missing:
        errors.append(f"{prefix}missing fields: {missing}")
    items = data.get("items")
    if items is not None and not isinstance(items, list):
        errors.append(f"{prefix}items must be a list")
        return errors
    seen_ids: set[str] = set()
    for index, item in enumerate(items or [], start=1):
        item_source = f"{source}:items[{index}]" if source else f"items[{index}]"
        errors.extend(validate_item(item, item_source))
        review_id = str(item.get("review_id", "")).strip()
        if review_id:
            if review_id in seen_ids:
                errors.append(f"{item_source}: duplicate review_id {review_id}")
            seen_ids.add(review_id)
    return errors


def summarize_review_queue(data: dict[str, Any]) -> dict[str, Any]:
    items = list(data.get("items") or [])
    open_count = sum(1 for item in items if str(item.get("status", "")).lower() in OPEN_STATUSES)
    decided_count = sum(1 for item in items if str(item.get("status", "")).lower() == "decided")
    return {
        "total_items": len(items),
        "open_items": open_count,
        "decided_items": decided_count,
    }


def build_review_item(
    *,
    review_id: str,
    type_: str,
    project_id: str,
    task_id: str,
    prompt: str,
    options: list[str],
    context_refs: list[str] | None = None,
    status: str = "open",
) -> dict[str, Any]:
    return {
        "review_id": review_id,
        "type": type_,
        "project_id": project_id,
        "task_id": task_id,
        "prompt": prompt,
        "options": options,
        "context_refs": context_refs or [],
        "status": status,
        "decision": None,
        "decided_at": None,
        "expires_at": None,
    }
