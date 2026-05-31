#!/usr/bin/env python3
"""Review helpers for LLM generation pipeline (manual vs auto-approve modes)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any


AUTO_APPROVE_REASON = "auto-approved for end-to-end real API pipeline test"


def resolve_review_mode(
    *,
    cli_review_mode: str | None = None,
    cli_auto_approve: bool | None = None,
    cli_skip_human: bool | None = None,
) -> dict[str, Any]:
    """Resolve review settings from CLI flags (highest) then environment."""
    env_auto = os.environ.get("AUTO_APPROVE_GENERATIONS", "").strip().lower() == "true"
    env_mode = os.environ.get("REVIEW_MODE", "manual").strip().lower()
    env_skip = os.environ.get("SKIP_HUMAN_REVIEW", "").strip().lower() == "true"

    auto_approve = env_auto if cli_auto_approve is None else cli_auto_approve
    review_mode = env_mode if not cli_review_mode else cli_review_mode.strip().lower()
    skip_human = env_skip if cli_skip_human is None else cli_skip_human

    if auto_approve or skip_human:
        review_mode = "auto"
    if review_mode == "auto":
        auto_approve = True
        skip_human = True

    return {
        "review_mode": review_mode,
        "auto_approve": auto_approve,
        "skip_human_review": skip_human,
    }


def build_auto_approve_metadata(
    *,
    generation_id: str,
    provider: str,
    model: str,
    quality_status: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    meta: dict[str, Any] = {
        "generation_id": generation_id,
        "review_status": "auto_approved",
        "review_mode": "auto",
        "reviewer": "agent",
        "review_reason": AUTO_APPROVE_REASON,
        "reviewed_at": now,
        "source": "real_api",
        "mock": False,
        "provider": provider,
        "model": model,
        "quality_status": quality_status,
        "created_at": now,
    }
    if extra:
        meta.update(extra)
    return meta


def build_pending_metadata(
    *,
    generation_id: str,
    provider: str,
    model: str,
    quality_status: str,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "generation_id": generation_id,
        "review_status": "pending",
        "review_mode": "manual",
        "reviewer": None,
        "review_reason": None,
        "reviewed_at": None,
        "source": "real_api",
        "mock": False,
        "provider": provider,
        "model": model,
        "quality_status": quality_status,
        "created_at": now,
    }


def assess_quality(content: str) -> str:
    text = (content or "").strip()
    if not text:
        return "failed_empty_output"
    if len(text) < 20:
        return "pass_with_issues"
    required_sections = ("##", "行动", "风险", "暂缓")
    hits = sum(1 for token in required_sections if token in text)
    if hits < 2 and "##" not in text:
        return "pass_with_issues"
    return "pass"


def should_auto_approve(settings: dict[str, Any]) -> bool:
    return bool(settings.get("auto_approve") or settings.get("skip_human_review"))
