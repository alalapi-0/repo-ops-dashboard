"""Tests for protocol_sync_report."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import protocol_sync_report as psr  # noqa: E402


def test_governance_status_detects_missing() -> None:
    repo = {
        "read_files": ["README.md", "docs/index.md"],
        "missing": ["AGENTS.md", "repo_protocol_standard.yaml"],
    }
    present, absent = psr.governance_status(repo)
    assert "README.md" in present
    assert "AGENTS.md" in absent
    assert "repo_protocol_standard.yaml" in absent
