"""Tests for run_eval_registry."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_eval_registry as eval_runner  # noqa: E402


def test_summarize_blocked_on_required_failure() -> None:
    outcomes = [
        eval_runner.EvalOutcome("a", "PASS", "ok", True),
        eval_runner.EvalOutcome("b", "FAIL", "bad", True),
    ]
    summary = eval_runner.summarize(outcomes)
    assert summary["verdict"] == "BLOCKED"
    assert summary["failed_required"] == 1


def test_run_registry_required_only_smoke(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    registry = root / "governance/evals/registry.yaml"
    outcomes = eval_runner.run_registry(
        root,
        registry,
        dry_run=True,
        skip_ui=True,
        required_only=True,
    )
    assert outcomes
    assert any(o.eval_id == "repo_protocol_exists" for o in outcomes)


def test_resolve_completion_report_uses_round_state() -> None:
    root = Path(__file__).resolve().parents[1]
    report = eval_runner.resolve_completion_report(root)
    assert report is None or report.name.endswith("_completion_report.md")
