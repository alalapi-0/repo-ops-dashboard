"""Tests for personal_os_integration_snapshot (no subprocess)."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import personal_os_integration_snapshot as integration  # noqa: E402


def test_count_projects() -> None:
    assert integration.count_projects({"projects": [{"id": "a"}, {"id": "b"}]}) == 2
    assert integration.count_projects({}) == 0


def test_budget_summary() -> None:
    summary = integration.budget_summary({"entries": [{"amount_usd": 10}, {"amount_usd": 5.5}]})
    assert summary["entry_count"] == 2
    assert summary["total_usd"] == 15.5


def test_build_snapshot_has_mock_modules() -> None:
    snap = integration.build_snapshot(
        round_state={"current_round": "round_63", "next_round": "maintenance_mode"},
        portfolio={"projects": [{}]},
        budget={"entries": []},
        digest_headline="- next：maintenance",
        mock_modules={"schedule": {"status": "mock", "note": "ics"}},
        architecture_complete=True,
    )
    assert snap["architecture_40_rounds_complete"] is True
    assert snap["mock_modules"]["schedule"]["status"] == "mock"
    assert snap["external_api_called"] is False
