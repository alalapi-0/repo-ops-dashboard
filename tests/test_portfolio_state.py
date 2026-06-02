"""Tests for portfolio state sync."""

from __future__ import annotations

from pathlib import Path

import sync_portfolio_state as sps
import yaml


def test_health_band_thresholds() -> None:
    assert sps.health_band(80) == "green"
    assert sps.health_band(50) == "yellow"
    assert sps.health_band(10) == "red"
    assert sps.health_band(None) == "unknown"


def test_portfolio_matches_registry_count() -> None:
    root = Path(__file__).resolve().parents[1]
    registry = yaml.safe_load((root / "governance" / "project_registry.yaml").read_text(encoding="utf-8")) or {}
    portfolio = yaml.safe_load((root / "governance" / "portfolio_state.yaml").read_text(encoding="utf-8")) or {}
    assert len(portfolio.get("projects", [])) == len(registry.get("projects", []))
    assert portfolio.get("summary", {}).get("total_projects") == len(registry.get("projects", []))
