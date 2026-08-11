"""Tests for agent_gate deterministic checks."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import agent_gate as gate


def test_gate_state_pass_when_empty() -> None:
    state = gate.GateState()
    assert state.verdict == gate.PASS


def test_gate_state_blocked_over_warning() -> None:
    state = gate.GateState()
    state.add("a", gate.WARNING, "warn")
    state.add("b", gate.BLOCKED, "block")
    assert state.verdict == gate.BLOCKED


def test_round_files_complete() -> None:
    root = Path(__file__).resolve().parents[1]
    state = gate.GateState()
    gate.check_round_docs_exist(state, root)
    assert any(f.check == "round_docs" and f.severity == gate.PASS for f in state.findings)


def test_installation_doc_exists() -> None:
    root = Path(__file__).resolve().parents[1]
    state = gate.GateState()
    gate.check_installation_doc(state, root)
    assert any(f.check == "installation_doc" and f.severity == gate.PASS for f in state.findings)


def test_example_fixtures_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    state = gate.GateState()
    gate.check_example_fixtures(state, root)
    assert any(f.check == "example_fixtures" and f.severity == gate.PASS for f in state.findings)


def test_report_rendering_is_in_memory() -> None:
    state = gate.GateState()
    state.add("sample", gate.PASS, "ok")
    text = gate.render_report(state)
    assert "# Agent Gate Report" in text
    assert "[PASS] `sample`: ok" in text


def test_default_gate_does_not_rewrite_report() -> None:
    root = Path(__file__).resolve().parents[1]
    report = root / "reports" / "agent_gate_report.md"
    before = report.read_bytes() if report.exists() else None
    completed = subprocess.run(
        [sys.executable, "scripts/agent_gate.py"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    after = report.read_bytes() if report.exists() else None
    assert completed.returncode in {0, 1, 2}
    assert "report=not-written" in completed.stdout
    assert after == before
