"""Tests for generate_handoff_packet."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import generate_handoff_packet as gen  # noqa: E402


def test_build_packet_from_example_task_spec() -> None:
    root = Path(__file__).resolve().parents[1]
    spec = gen.load_yaml(root / "governance/task_specs/example_task_spec.yaml")
    packet = gen.build_packet(spec, repo_root=root)
    assert packet["handoff_id"].startswith("handoff_")
    assert packet["target_agent"] == "Cursor"
    assert packet["return_contract"]["validation_commands"]
