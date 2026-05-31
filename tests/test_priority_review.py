"""Tests for priority_review scoring."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import priority_review as pr  # noqa: E402


def test_score_repo_meta_ops_high() -> None:
    factors = {
        "type_scores": {"meta_ops": 25, "unknown": 5},
        "health_weight": 0.35,
        "blocker_penalty": 25,
        "thresholds": {"high": 55, "medium": 30},
    }
    repo = {
        "type": "meta_ops",
        "health_score": 90,
        "blockers": [],
        "archive_candidate": False,
        "freeze_candidate": False,
    }
    score, suggested, _ = pr.score_repo(repo, factors)
    assert score >= 55
    assert suggested == "high"


def test_human_hint_overrides_suggested() -> None:
    status = {
        "repos": [
            {
                "name": "demo",
                "type": "unknown",
                "health_score": 10,
                "priority": "low",
                "blockers": [],
                "archive_candidate": False,
                "freeze_candidate": False,
            }
        ]
    }
    factors = {"type_scores": {"unknown": 5}, "health_weight": 0.35, "thresholds": {"high": 55, "medium": 30}}
    board = pr.build_board(status, factors, {"demo": "high"})
    row = board["repos"][0]
    assert row["final_priority"] == "high"
    assert row["priority_source"] == "human_override"
