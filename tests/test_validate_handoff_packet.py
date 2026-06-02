"""Tests for validate_handoff_packet."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import validate_handoff_packet as handoff  # noqa: E402


def test_example_handoff_packet_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "governance/handoffs/example_handoff_packet.yaml"
    errors = handoff.validate_handoff_file(path)
    assert errors == []


def test_missing_working_directory_fails() -> None:
    data = {"handoff_id": "handoff_x", "target_agent": "Cursor", "working_directory": ""}
    errors = handoff.validate_handoff_packet(data)
    assert any("working_directory" in e for e in errors)
