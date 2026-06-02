"""Tests for proof_of_work validation and registry sync."""

from __future__ import annotations

import json
from pathlib import Path

import sync_proof_of_work_registry as pow_sync
import validate_proof_of_work as vpw


def test_validate_example_proof() -> None:
    root = Path(__file__).resolve().parents[1]
    data = vpw.read_proof_of_work(root / "governance" / "proof_of_work" / "example_proof_of_work.json")
    assert not vpw.validate_proof_of_work(data)


def test_validate_detects_missing_field() -> None:
    errors = vpw.validate_proof_of_work({"task_id": "task_x"})
    assert errors


def test_discover_excludes_template() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = vpw.discover_proof_files(root / "governance" / "proof_of_work")
    names = {p.name for p in paths}
    assert "proof_of_work.template.json" not in names
    assert "example_proof_of_work.json" in names


def test_build_registry_includes_example() -> None:
    root = Path(__file__).resolve().parents[1]
    payload, errors = pow_sync.build_registry(root, root / "governance" / "proof_of_work")
    assert not errors
    task_ids = {r["task_id"] for r in payload["records"]}
    assert "task_light_novel_governance_prompt_001" in task_ids


def test_read_proof_of_work_cli_path() -> None:
    root = Path(__file__).resolve().parents[1]
    example = root / "governance" / "proof_of_work" / "example_proof_of_work.json"
    raw = json.loads(example.read_text(encoding="utf-8"))
    assert raw["task_id"].startswith("task_")
