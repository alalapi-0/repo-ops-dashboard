"""Tests for review_queue validation and read helpers."""

from __future__ import annotations

from pathlib import Path

import validate_review_queue as vrq


def test_validate_live_review_queue() -> None:
    root = Path(__file__).resolve().parents[1]
    queue = vrq.read_review_queue(root / "governance" / "review_queue.yaml")
    assert not vrq.validate_review_queue(queue)


def test_validate_example_review_queue() -> None:
    root = Path(__file__).resolve().parents[1]
    queue = vrq.read_review_queue(root / "governance" / "review_queue.example.yaml")
    assert not vrq.validate_review_queue(queue)


def test_open_item_requires_null_decision() -> None:
    item = vrq.build_review_item(
        review_id="rq_test",
        type_="governance_policy",
        project_id="repo_ops_dashboard",
        task_id="task_x",
        prompt="test?",
        options=["yes", "no"],
    )
    item["decision"] = "yes"
    errors = vrq.validate_item(item)
    assert any("decision=null" in err for err in errors)


def test_decided_item_requires_decision() -> None:
    item = vrq.build_review_item(
        review_id="rq_test",
        type_="governance_policy",
        project_id="repo_ops_dashboard",
        task_id="task_x",
        prompt="test?",
        options=["yes", "no"],
        status="decided",
    )
    errors = vrq.validate_item(item)
    assert any("requires decision" in err for err in errors)


def test_summarize_counts_open_items() -> None:
    root = Path(__file__).resolve().parents[1]
    queue = vrq.read_review_queue(root / "governance" / "review_queue.yaml")
    summary = vrq.summarize_review_queue(queue)
    assert summary["total_items"] >= 5
    assert summary["open_items"] >= 5
    assert summary["decided_items"] == 0
