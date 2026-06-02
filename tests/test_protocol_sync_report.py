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
    present, absent = psr.governance_status(repo, psr.GOVERNANCE_FILES)
    assert "README.md" in present
    assert "AGENTS.md" in absent
    assert "repo_protocol_standard.yaml" in absent


def test_suggest_priority_high_for_agents_missing() -> None:
    assert psr.suggest_priority(["AGENTS.md"], {"AGENTS.md"}) == "high"
    assert psr.suggest_priority(["CHANGELOG.md"], {"AGENTS.md"}) == "medium"
    assert psr.suggest_priority([], {"AGENTS.md"}) == "none"


def test_build_yaml_payload_counts_need_sync() -> None:
    snapshots = {
        "repos": [
            {"name": "a", "status": "active", "read_files": ["README.md"], "missing": ["AGENTS.md"]},
            {"name": "b", "status": "active", "read_files": psr.GOVERNANCE_FILES, "missing": []},
            {"name": "c", "status": "missing", "read_files": [], "missing": psr.GOVERNANCE_FILES},
        ]
    }
    payload = psr.build_yaml_payload(
        snapshots,
        "0.3.0",
        files=psr.GOVERNANCE_FILES,
        skip_statuses={"missing"},
        high_missing={"AGENTS.md"},
        status_source="data/repo_snapshots.example.json",
    )
    assert payload["summary"]["need_sync"] == 1
    assert payload["summary"]["high_priority"] == 1
    assert payload["summary"]["skipped"] == 1
