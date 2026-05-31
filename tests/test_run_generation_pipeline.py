"""Tests for run_generation_pipeline (no real API)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_generation_pipeline as pipeline  # noqa: E402


def test_build_prompt_variants_count() -> None:
    status = {
        "repos": [
            {"name": "a", "priority": "high", "blockers": []},
            {"name": "b", "priority": "low", "blockers": ["x"]},
        ]
    }
    variants = pipeline.build_prompt_variants(status, "daily", "brief", 3)
    assert len(variants) == 3
    assert variants[0][0] == "daily_summary"
    assert "a" in variants[1][0]


def test_update_index_appends(tmp_path: Path) -> None:
    root = tmp_path / "generations"
    root.mkdir()
    entries = [
        {
            "generation_id": "g1",
            "label": "daily_summary",
            "review_status": "auto_approved",
            "quality_status": "pass",
            "approved_path": "data/generations/approved/g1",
        }
    ]
    index_path = pipeline.update_index(root, entries, "round_test")
    data = json.loads(index_path.read_text(encoding="utf-8"))
    assert len(data["generations"]) == 1
    assert data["last_round"] == "round_test"


def test_main_dry_run() -> None:
    argv = ["run_generation_pipeline.py", "--dry-run"]
    with mock.patch.object(sys, "argv", argv):
        assert pipeline.main() == 0
