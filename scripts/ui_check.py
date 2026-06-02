#!/usr/bin/env python3
"""Local Dashboard UI check via Playwright (file:// only, no external network)."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

PLAYWRIGHT_INSTALL_HINT = """\
Please run:
pip install -r requirements-dev.txt
python3 -m playwright install chromium
"""

ALLOWED_HTTP_HOSTS = frozenset({"127.0.0.1", "localhost"})


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local dashboard UI with Playwright")
    parser.add_argument("--file", default="dashboard/index.html", help="Dashboard HTML file path")
    parser.add_argument(
        "--url",
        default="",
        help="Optional page URL (e.g. http://127.0.0.1:8765/dashboard/index.html); overrides --file",
    )
    parser.add_argument(
        "--screenshot",
        default="reports/ui_screenshots/dashboard.png",
        help="Screenshot output path",
    )
    parser.add_argument("--headless", default="true", help="Run browser headless (true/false)")
    parser.add_argument(
        "--report",
        default="reports/ui_check_report.md",
        help="Markdown report output path",
    )
    return parser.parse_args()


def file_uri(path: Path) -> str:
    return path.resolve().as_uri()


def validate_target_url(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme == "file":
        local_path = Path(unquote(parsed.path))
        if not local_path.exists():
            return f"file URL path does not exist: {local_path}"
        return None
    if parsed.scheme == "http":
        host = (parsed.hostname or "").lower()
        if host not in ALLOWED_HTTP_HOSTS:
            return f"HTTP host not allowed: {host!r} (allowed: {sorted(ALLOWED_HTTP_HOSTS)})"
        return None
    return f"URL scheme not allowed: {parsed.scheme!r}"


def resolve_page_url(html_path: Path, url_override: str) -> str:
    if url_override.strip():
        return url_override.strip()
    return file_uri(html_path)


def write_report(
    report_path: Path,
    *,
    passed: bool,
    checks: list[dict[str, Any]],
    warnings: list[str],
    errors: list[str],
    screenshot: Path | None,
    page_url: str = "",
    console_messages: list[str] | None = None,
    failed_requests: list[str] | None = None,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    status = "PASS" if passed and not errors else "FAIL"
    lines = [
        "# UI Check Report",
        "",
        f"- generated_at: {datetime.now(timezone.utc).isoformat()}",
        f"- status: {status}",
        f"- page_url: {page_url or 'n/a'}",
        f"- screenshot: {screenshot if screenshot else 'none'}",
        "",
        "## Checks",
    ]
    for item in checks:
        mark = "PASS" if item.get("ok") else "FAIL"
        lines.append(f"- [{mark}] {item.get('name')}: {item.get('detail')}")
    if console_messages:
        lines.extend(["", "## Console"])
        for msg in console_messages:
            lines.append(f"- {msg}")
    if failed_requests:
        lines.extend(["", "## Network failures"])
        for req in failed_requests:
            lines.append(f"- {req}")
    if warnings:
        lines.extend(["", "## Warnings"])
        for w in warnings:
            lines.append(f"- {w}")
    if errors:
        lines.extend(["", "## Errors"])
        for e in errors:
            lines.append(f"- {e}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_playwright_checks(
    page: Any,
    *,
    checks: list[dict[str, Any]],
    warnings: list[str],
    errors: list[str],
    console_errors: list[str],
    failed_requests: list[str],
) -> None:
    title = page.title()
    title_ok = "Repo Ops Dashboard" in title
    checks.append({"name": "page_title", "ok": title_ok, "detail": f"title={title!r}"})
    if not title_ok:
        errors.append("Page title does not contain 'Repo Ops Dashboard'")

    container = page.locator("main.container, main, .container").first
    container_count = container.count()
    container_ok = container_count > 0
    checks.append(
        {
            "name": "dashboard_container",
            "ok": container_ok,
            "detail": f"found={container_count > 0}",
        }
    )
    if not container_ok:
        errors.append("No dashboard container (main.container / main / .container) found")

    cards = page.locator(".repo-card")
    card_count = cards.count()
    checks.append({"name": "repo_cards", "ok": True, "detail": f"count={card_count}"})
    if card_count == 0:
        warnings.append("No .repo-card elements found; dashboard may be empty or not yet generated")

    filters = page.locator(".filters select")
    filter_count = filters.count()
    filter_ok = filter_count >= 3
    checks.append({"name": "dashboard_filters", "ok": filter_ok, "detail": f"count={filter_count}"})
    if not filter_ok:
        warnings.append("Dashboard filters missing or incomplete")
    elif filter_count > 0:
        first_filter = filters.first
        options = first_filter.locator("option")
        if options.count() > 1:
            first_filter.select_option(index=1)
            page.wait_for_timeout(150)
            checks.append(
                {
                    "name": "filter_interaction",
                    "ok": True,
                    "detail": "first filter changed to second option",
                }
            )

    copy_buttons = page.locator(".copy-prompt")
    copy_count = copy_buttons.count()
    checks.append({"name": "copy_prompt_buttons", "ok": copy_count > 0, "detail": f"count={copy_count}"})
    if copy_count == 0:
        warnings.append("No copy-prompt buttons found on repo cards")
    else:
        visible_copy = page.locator(".copy-prompt:visible")
        if visible_copy.count() > 0:
            visible_copy.first.scroll_into_view_if_needed()
            visible_copy.first.click(timeout=5000)
            checks.append({"name": "copy_prompt_click", "ok": True, "detail": "first visible copy button clicked"})
        else:
            warnings.append("Copy-prompt buttons exist but none are visible in viewport")

    human_notes = page.locator(".human-notes[data-human-notes-ready='true']")
    hn_count = human_notes.count()
    checks.append({"name": "human_notes_section", "ok": hn_count > 0, "detail": f"count={hn_count}"})
    if hn_count == 0:
        warnings.append("No human-notes section; run generate_dashboard with human_notes.example.json")

    gov_v2 = page.locator(".governance-v2[data-dashboard-v2-ready='true']")
    gov_count = gov_v2.count()
    checks.append({"name": "governance_v2_section", "ok": gov_count > 0, "detail": f"count={gov_count}"})
    if gov_count == 0:
        warnings.append("No governance-v2 section; run generate_dashboard with portfolio/task/review YAML")

    for panel in ("portfolio_state", "task_queue", "review_queue", "blockers"):
        loc = page.locator(f".gov-panel[data-panel='{panel}']")
        panel_ok = loc.count() > 0
        checks.append({"name": f"gov_panel_{panel}", "ok": panel_ok, "detail": f"count={loc.count()}"})
        if not panel_ok:
            warnings.append(f"Missing governance panel: {panel}")

    console_ok = len(console_errors) == 0
    checks.append(
        {
            "name": "console_no_errors",
            "ok": console_ok,
            "detail": f"errors={len(console_errors)}",
        }
    )
    if not console_ok:
        for item in console_errors:
            errors.append(f"Console error: {item}")

    network_ok = len(failed_requests) == 0
    checks.append(
        {
            "name": "network_no_failed_requests",
            "ok": network_ok,
            "detail": f"failed={len(failed_requests)}",
        }
    )
    if not network_ok:
        for item in failed_requests:
            errors.append(f"Request failed: {item}")

    current = page.url
    parsed = urlparse(current)
    if parsed.scheme == "file":
        local_path = Path(unquote(parsed.path))
        if not local_path.resolve().exists():
            warnings.append(f"Unexpected file URL resolved path: {local_path}")
    elif parsed.scheme == "http":
        host = (parsed.hostname or "").lower()
        if host not in ALLOWED_HTTP_HOSTS:
            errors.append(f"Unexpected HTTP host after navigation: {host}")
    elif parsed.scheme not in {"", "file"}:
        errors.append(f"Unexpected non-local navigation: {current}")


def main() -> int:
    args = parse_args()
    html_path = Path(args.file)
    screenshot_path = Path(args.screenshot)
    report_path = Path(args.report)
    headless = parse_bool(args.headless)

    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []

    if not html_path.exists() and not args.url.strip():
        msg = f"Dashboard file not found: {html_path}"
        errors.append(msg)
        write_report(report_path, passed=False, checks=checks, warnings=warnings, errors=errors, screenshot=None)
        print(f"[error] {msg}", file=sys.stderr)
        return 1

    page_url = resolve_page_url(html_path, args.url)
    url_error = validate_target_url(page_url)
    if url_error:
        errors.append(url_error)
        write_report(
            report_path,
            passed=False,
            checks=checks,
            warnings=warnings,
            errors=errors,
            screenshot=None,
            page_url=page_url,
        )
        print(f"[error] {url_error}", file=sys.stderr)
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(PLAYWRIGHT_INSTALL_HINT, file=sys.stderr)
        write_report(
            report_path,
            passed=False,
            checks=checks,
            warnings=["Playwright not installed"],
            errors=["ImportError: playwright"],
            screenshot=None,
            page_url=page_url,
        )
        return 2

    screenshot_taken: Path | None = None
    console_errors: list[str] = []
    failed_requests: list[str] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()

            def on_console(msg: Any) -> None:
                if msg.type == "error":
                    console_errors.append(msg.text)

            def on_request_failed(request: Any) -> None:
                failure = request.failure
                reason = failure if isinstance(failure, str) else getattr(failure, "error_text", str(failure))
                failed_requests.append(f"{request.method} {request.url} — {reason}")

            page.on("console", on_console)
            page.on("requestfailed", on_request_failed)

            page.goto(page_url, wait_until="domcontentloaded")
            run_playwright_checks(
                page,
                checks=checks,
                warnings=warnings,
                errors=errors,
                console_errors=console_errors,
                failed_requests=failed_requests,
            )

            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot_path), full_page=True)
            screenshot_taken = screenshot_path
            checks.append({"name": "screenshot", "ok": True, "detail": str(screenshot_path)})

            browser.close()
    except Exception as exc:  # pragma: no cover
        errors.append(f"Playwright error: {exc}")
        write_report(
            report_path,
            passed=False,
            checks=checks,
            warnings=warnings,
            errors=errors,
            screenshot=screenshot_taken,
            page_url=page_url,
            console_messages=console_errors or None,
            failed_requests=failed_requests or None,
        )
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    passed = not errors
    write_report(
        report_path,
        passed=passed,
        checks=checks,
        warnings=warnings,
        errors=errors,
        screenshot=screenshot_taken,
        page_url=page_url,
        console_messages=console_errors or None,
        failed_requests=failed_requests or None,
    )
    print(f"[ui_check] status={'PASS' if passed else 'FAIL'} report={report_path}")
    for w in warnings:
        print(f"[warning] {w}")
    for e in errors:
        print(f"[error] {e}", file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
