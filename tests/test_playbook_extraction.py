"""Tests for playbook candidate extraction."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import extract_playbook_candidates as extract  # noqa: E402
import validate_playbook_extraction_policy as policy_mod  # noqa: E402


def test_policy_file_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "config" / "playbook_extraction_policy.yaml"
    errors = policy_mod.validate_playbook_extraction_policy_file(path)
    assert errors == []


def test_record_eligible_completed() -> None:
    record = {"status": "completed", "tests_passed": False, "known_issue_count": 1}
    selection = {"status_allowlist": ["completed"], "require_tests_passed": False}
    assert extract.record_eligible(record, selection) is True
