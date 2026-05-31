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


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local dashboard UI with Playwright")
    parser.add_argument("--file", default="dashboard/index.html", help="Dashboard HTML file path")
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


def write_report(
    report_path: Path,
    *,
    passed: bool,
    checks: list[dict[str, Any]],
    warnings: list[str],
    errors: list[str],
    screenshot: Path | None,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    status = "PASS" if passed and not errors else "FAIL"
    lines = [
        "# UI Check Report",
        "",
        f"- generated_at: {datetime.now(timezone.utc).isoformat()}",
        f"- status: {status}",
        f"- screenshot: {screenshot if screenshot else 'none'}",
        "",
        "## Checks",
    ]
    for item in checks:
        mark = "PASS" if item.get("ok") else "FAIL"
        lines.append(f"- [{mark}] {item.get('name')}: {item.get('detail')}")
    if warnings:
        lines.extend(["", "## Warnings"])
        for w in warnings:
            lines.append(f"- {w}")
    if errors:
        lines.extend(["", "## Errors"])
        for e in errors:
            lines.append(f"- {e}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    html_path = Path(args.file)
    screenshot_path = Path(args.screenshot)
    report_path = Path(args.report)
    headless = parse_bool(args.headless)

    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []

    if not html_path.exists():
        msg = f"Dashboard file not found: {html_path}"
        errors.append(msg)
        write_report(report_path, passed=False, checks=checks, warnings=warnings, errors=errors, screenshot=None)
        print(f"[error] {msg}", file=sys.stderr)
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
        )
        return 2

    url = file_uri(html_path)
    screenshot_taken: Path | None = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")

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

            copy_buttons = page.locator(".copy-prompt")
            copy_count = copy_buttons.count()
            checks.append({"name": "copy_prompt_buttons", "ok": copy_count > 0, "detail": f"count={copy_count}"})
            if copy_count == 0:
                warnings.append("No copy-prompt buttons found on repo cards")

            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot_path), full_page=True)
            screenshot_taken = screenshot_path
            checks.append({"name": "screenshot", "ok": True, "detail": str(screenshot_path)})

            # Ensure no unexpected external navigation
            current = page.url
            parsed = urlparse(current)
            if parsed.scheme == "file":
                local_path = Path(unquote(parsed.path))
                if not local_path.resolve().exists():
                    warnings.append(f"Unexpected file URL resolved path: {local_path}")
            elif parsed.scheme not in {"", "file"}:
                errors.append(f"Unexpected non-file navigation: {current}")

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
    )
    print(f"[ui_check] status={'PASS' if passed else 'FAIL'} report={report_path}")
    for w in warnings:
        print(f"[warning] {w}")
    for e in errors:
        print(f"[error] {e}", file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
