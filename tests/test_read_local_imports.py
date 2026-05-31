"""Tests for read_local_imports."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import read_local_imports as li  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def test_summarize_ics_example() -> None:
    lines = li.summarize_ics(ROOT / "data/sample_calendar.example.ics")
    assert any("Repo ops" in line for line in lines)


def test_summarize_csv_example() -> None:
    lines = li.summarize_csv(ROOT / "data/sample_finance.example.csv")
    assert any("行数" in line for line in lines)
