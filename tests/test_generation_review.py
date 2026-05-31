"""Tests for generation_review helpers."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import generation_review as gr  # noqa: E402


def test_resolve_review_mode_manual_by_default() -> None:
    settings = gr.resolve_review_mode()
    assert settings["review_mode"] == "manual"
    assert settings["auto_approve"] is False


def test_resolve_review_mode_auto_from_cli() -> None:
    settings = gr.resolve_review_mode(cli_auto_approve=True, cli_review_mode="auto")
    assert settings["review_mode"] == "auto"
    assert settings["auto_approve"] is True
    assert settings["skip_human_review"] is True


def test_build_auto_approve_metadata_schema() -> None:
    meta = gr.build_auto_approve_metadata(
        generation_id="g1",
        provider="openrouter",
        model="deepseek/deepseek-v4-pro",
        quality_status="pass",
    )
    assert meta["review_status"] == "auto_approved"
    assert meta["review_mode"] == "auto"
    assert meta["reviewer"] == "agent"
    assert meta["mock"] is False
    assert meta["source"] == "real_api"
    assert "reviewed_at" in meta


def test_assess_quality_empty() -> None:
    assert gr.assess_quality("") == "failed_empty_output"


def test_assess_quality_pass() -> None:
    text = "## 今日三条行动\n- 推进 demo\n\n## 风险提醒\n- 无"
    assert gr.assess_quality(text) == "pass"
