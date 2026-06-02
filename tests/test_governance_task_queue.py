"""Tests for governance task queue sync and task_spec reading."""

from __future__ import annotations

from pathlib import Path

import sync_governance_task_queue as gtq
import yaml


def test_validate_task_spec_requires_fields() -> None:
    errors = gtq.validate_task_spec({"task_id": "task_x", "project_id": "p"})
    assert errors
    assert any("missing fields" in err for err in errors)


def test_validate_task_spec_passes_example() -> None:
    root = Path(__file__).resolve().parents[1]
    spec = gtq.read_task_spec(root / "governance" / "task_specs" / "example_task_spec.yaml")
    assert not gtq.validate_task_spec(spec)


def test_discover_excludes_template() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = gtq.discover_task_specs(root / "governance" / "task_specs")
    names = {p.name for p in paths}
    assert "task_spec.template.yaml" not in names
    assert "example_task_spec.yaml" in names


def test_build_queue_matches_example_task() -> None:
    root = Path(__file__).resolve().parents[1]
    payload, errors = gtq.build_queue(root, root / "governance" / "task_specs")
    assert not errors
    assert payload["summary"]["total_tasks"] >= 1
    task_ids = {t["task_id"] for t in payload["tasks"]}
    assert "task_light_novel_governance_prompt_001" in task_ids


def test_queue_file_exists_after_sync() -> None:
    root = Path(__file__).resolve().parents[1]
    queue_path = root / "governance" / "governance_task_queue.yaml"
    assert queue_path.exists()
    queue = yaml.safe_load(queue_path.read_text(encoding="utf-8")) or {}
    assert queue.get("summary", {}).get("total_tasks") >= 1
