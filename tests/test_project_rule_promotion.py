"""Tests for project rule promotion policy and planner."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import promote_project_rule as promote  # noqa: E402
import validate_project_rule_promotion_policy as policy_mod  # noqa: E402


def test_policy_file_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "config" / "project_rule_promotion_policy.yaml"
    errors = policy_mod.validate_project_rule_promotion_policy_file(path)
    assert errors == []


def test_build_proposal_from_candidate() -> None:
    candidate = {
        "candidate_id": "playbook_demo",
        "project_id": "demo",
        "source_task_id": "task_demo",
        "status": "proposed",
        "kind": "playbook",
        "context_refs": ["governance/playbooks/"],
    }
    proposal = promote.build_proposal(candidate, {"id_prefix": "rq_promo_", "review_type": "project_rule_promotion"}, now="2026-06-03T00:00:00+00:00")
    assert proposal["review_id"] == "rq_promo_demo"
    assert proposal["status"] == "pending_human_merge"
