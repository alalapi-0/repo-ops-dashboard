#!/usr/bin/env python3
"""Compute impact × urgency × unblock - cost - risk priority scores."""

from __future__ import annotations

from typing import Any


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def score_impact(repo: dict[str, Any], cfg: dict[str, Any]) -> int:
    repo_type = str(repo.get("type", "unknown"))
    type_impact = dict(cfg.get("type_impact", {}))
    base = int(type_impact.get(repo_type, type_impact.get("unknown", 3)))
    divisor = int(cfg.get("health_divisor", 20)) or 20
    health_bonus = int(round(int(repo.get("health_score", 0)) / divisor))
    if repo.get("registry_matched"):
        base += int(cfg.get("registry_match_bonus", 0))
    return _clamp(base + health_bonus, 0, int(cfg.get("max", 10)))


def score_urgency(repo: dict[str, Any], cfg: dict[str, Any]) -> int:
    value = int(cfg.get("baseline", 5))
    if repo.get("blockers"):
        value += int(cfg.get("blocker_boost", 0))
    if repo.get("freeze_candidate"):
        value += int(cfg.get("freeze_boost", 0))
    status = str(repo.get("status", ""))
    if status in {"missing", "empty"}:
        value += int(cfg.get("path_missing_boost", 0))
    return _clamp(value, 0, int(cfg.get("max", 10)))


def score_unblock(repo: dict[str, Any], cfg: dict[str, Any]) -> int:
    if repo.get("archive_candidate"):
        return 0
    if repo.get("blockers"):
        return _clamp(int(cfg.get("with_blockers", 2)), 0, int(cfg.get("max", 10)))
    value = int(cfg.get("baseline", 6))
    if repo.get("round_next"):
        value += int(cfg.get("round_next_bonus", 0))
    if repo.get("next_actions"):
        value += int(cfg.get("next_action_bonus", 0))
    if not repo.get("warnings"):
        value += int(cfg.get("clean_warnings_bonus", 0))
    return _clamp(value, 0, int(cfg.get("max", 10)))


def score_cost(repo: dict[str, Any], cfg: dict[str, Any]) -> int:
    warnings = list(repo.get("warnings") or [])
    cost = min(len(warnings), 5) * int(cfg.get("warning_each", 0))
    if repo.get("freeze_candidate"):
        cost += int(cfg.get("freeze_penalty", 0))
    return min(cost, int(cfg.get("max", 50)))


def score_risk(repo: dict[str, Any], cfg: dict[str, Any]) -> int:
    risk = 0
    if repo.get("archive_candidate"):
        risk += int(cfg.get("archive_penalty", 0))
    threshold = int(cfg.get("low_health_threshold", 30))
    if int(repo.get("health_score", 0)) < threshold:
        risk += int(cfg.get("low_health_penalty", 0))
    return min(risk, int(cfg.get("max", 50)))


def compute_priority_score(repo: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    """Return priority_score, breakdown, and score_band (high/medium/low)."""
    factors = dict(policy.get("factors", {}))
    formula = dict(policy.get("formula", {}))
    scale = int(formula.get("product_scale", 1000)) or 1000

    impact = score_impact(repo, dict(factors.get("impact", {})))
    urgency = score_urgency(repo, dict(factors.get("urgency", {})))
    unblock = score_unblock(repo, dict(factors.get("unblock", {})))
    cost = score_cost(repo, dict(factors.get("cost", {})))
    risk = score_risk(repo, dict(factors.get("risk", {})))

    product = impact * urgency * unblock
    total = max(0, int(round(product / scale - cost - risk)))

    bands = dict(policy.get("priority_bands", {}))
    high_cut = int(bands.get("high", 40))
    medium_cut = int(bands.get("medium", 15))
    if total >= high_cut:
        band = "high"
    elif total >= medium_cut:
        band = "medium"
    else:
        band = "low"

    return {
        "priority_score": total,
        "priority_score_band": band,
        "priority_score_breakdown": {
            "impact": impact,
            "urgency": urgency,
            "unblock": unblock,
            "cost": cost,
            "risk": risk,
            "product": product,
            "formula": str(formula.get("expression", "")),
        },
    }
