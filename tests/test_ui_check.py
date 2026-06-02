"""Tests for ui_check helpers (no browser required)."""

from __future__ import annotations

from pathlib import Path

import ui_check as mod


def test_parse_bool() -> None:
    assert mod.parse_bool("true") is True
    assert mod.parse_bool("FALSE") is False
    assert mod.parse_bool("yes") is True


def test_validate_target_url_file_missing() -> None:
    err = mod.validate_target_url("file:///nonexistent/path/dashboard.html")
    assert err is not None


def test_validate_target_url_http_localhost_ok() -> None:
    assert mod.validate_target_url("http://127.0.0.1:8765/dashboard/") is None


def test_validate_target_url_external_blocked() -> None:
    err = mod.validate_target_url("https://example.com/dashboard")
    assert err is not None


def test_resolve_page_url_prefers_override() -> None:
    html = Path("dashboard/index.html")
    url = mod.resolve_page_url(html, "http://127.0.0.1:8765/dashboard/")
    assert url.startswith("http://127.0.0.1")


def test_write_report_includes_console_section(tmp_path: Path) -> None:
    report = tmp_path / "ui.md"
    mod.write_report(
        report,
        passed=True,
        checks=[{"name": "page_title", "ok": True, "detail": "ok"}],
        warnings=[],
        errors=[],
        screenshot=None,
        page_url="file:///tmp/index.html",
        console_messages=["[error] none"],
    )
    text = report.read_text(encoding="utf-8")
    assert "## Console" in text
    assert "page_url:" in text


def test_validate_ui_check_policy_live_config() -> None:
    from validate_ui_check_policy import read_ui_check_policy, validate_ui_check_policy

    root = Path(__file__).resolve().parents[1]
    live = root / "config" / "ui_check_policy.yaml"
    data = read_ui_check_policy(live)
    assert validate_ui_check_policy(data, live.name) == []
