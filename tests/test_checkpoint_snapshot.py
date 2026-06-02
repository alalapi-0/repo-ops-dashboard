"""Tests for portfolio checkpoint snapshot policy and planner."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import snapshot_portfolio_checkpoint as snap  # noqa: E402
import validate_checkpoint_snapshot_policy as policy_mod  # noqa: E402


def test_policy_file_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "config" / "checkpoint_snapshot_policy.yaml"
    errors = policy_mod.validate_checkpoint_snapshot_policy_file(path)
    assert errors == []


def test_build_checkpoint_id_prefix() -> None:
    from datetime import datetime, timezone

    ts = datetime(2026, 6, 3, 12, 0, 0, tzinfo=timezone.utc)
    cid = snap.build_checkpoint_id("ckpt_portfolio_", ts)
    assert cid.startswith("ckpt_portfolio_")
    assert "20260603" in cid
