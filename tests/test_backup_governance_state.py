"""Tests for backup_governance_state (no subprocess)."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import backup_governance_state as backup  # noqa: E402


def test_build_backup_id_format() -> None:
    from datetime import datetime, timezone

    ts = datetime(2026, 6, 3, 12, 0, 0, tzinfo=timezone.utc)
    bid = backup.build_backup_id("backup_gov_", ts)
    assert bid.startswith("backup_gov_")
    assert "20260603" in bid


def test_collect_paths_finds_portfolio() -> None:
    root = Path(__file__).resolve().parents[1]
    found, missing = backup.collect_paths(root, ["governance/portfolio_state.yaml", "nonexistent.yaml"])
    assert len(found) == 1
    assert "nonexistent.yaml" in missing


def test_render_report_includes_hitl() -> None:
    text = backup.render_report(
        backup_id="backup_gov_test",
        files=["governance/portfolio_state.yaml"],
        missing=[],
        backup_dir="governance/backups/backup_gov_test",
        dry_run=True,
    )
    assert "HITL" in text
    assert "dry-run" in text
