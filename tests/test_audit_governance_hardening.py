"""Tests for audit_governance_hardening (no subprocess)."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import audit_governance_hardening as audit  # noqa: E402


def test_check_denylist_passes_with_config() -> None:
    root = Path(__file__).resolve().parents[1]
    sev, msg = audit.check_denylist(root, "config/managed_files.yaml")
    assert sev == "PASS"
    assert "denylist" in msg


def test_render_report_includes_verdict() -> None:
    text = audit.render_report(
        findings=[("denylist", "PASS", "ok"), ("round_docs", "PASS", "ok")],
        dry_run=True,
    )
    assert "Verdict: PASS" in text
    assert "dry-run" in text


def test_check_protocol_agents_alignment() -> None:
    root = Path(__file__).resolve().parents[1]
    sev, _ = audit.check_protocol_agents_alignment(root, "repo_protocol_standard.yaml", "AGENTS.md")
    assert sev in {"PASS", "WARNING"}
