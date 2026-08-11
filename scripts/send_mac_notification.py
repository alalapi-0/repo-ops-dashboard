#!/usr/bin/env python3
"""Mac local notification for daily suggestions and blockers (dry-run payload default)."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

DEFAULT_POLICY = "config/mac_notification_policy.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def redact_paths(text: str) -> str:
    return re.sub(r"/Users/[^\s|]+/", "[local-path]/", text)


def extract_brief_excerpt(brief_text: str, *, max_chars: int = 220) -> str:
    if not brief_text.strip():
        return "（暂无每日简报）"
    for heading in ("## 短提醒", "## 今日最该推进（1–3 仓）", "## 风险提醒"):
        match = re.search(rf"{re.escape(heading)}\n\n(.*?)(?:\n## |\n---\n|\Z)", brief_text, re.DOTALL)
        if match:
            excerpt = redact_paths(match.group(1).strip())
            if excerpt:
                if len(excerpt) > max_chars:
                    return excerpt[: max_chars - 1] + "…"
                return excerpt
    fallback = redact_paths(brief_text.strip())
    if len(fallback) > max_chars:
        return fallback[: max_chars - 1] + "…"
    return fallback or "（暂无每日简报）"


def collect_blockers(status_data: dict[str, Any], *, limit: int = 3) -> list[str]:
    items: list[str] = []
    for repo in status_data.get("repos", []):
        blockers = repo.get("blockers") or []
        if not blockers:
            continue
        name = str(repo.get("name", "unknown"))
        first = redact_paths(str(blockers[0]))
        items.append(f"{name}: {first}")
        if len(items) >= limit:
            break
    return items


def should_skip_osascript(policy: dict[str, Any]) -> tuple[bool, str]:
    delivery = policy.get("delivery", {})
    skip_envs = {str(v).upper() for v in delivery.get("skip_osascript_when", [])}
    if platform.system() != "Darwin":
        return True, "non_darwin"
    for key in ("CI", "GITHUB_ACTIONS"):
        if key in skip_envs and os.environ.get(key):
            return True, key.lower()
    return False, ""


def build_payload(
    *,
    policy: dict[str, Any],
    brief_excerpt: str,
    blockers: list[str],
    for_send: bool,
) -> dict[str, Any]:
    content = policy.get("content", {})
    title = str(content.get("title", "Repo Ops"))
    body_parts = [brief_excerpt]
    if content.get("include_blockers", True) and blockers:
        body_parts.append("Blockers: " + "; ".join(blockers))
    body = "\n".join(body_parts)
    max_chars = int(content.get("max_body_chars", 220))
    if len(body) > max_chars:
        body = body[: max_chars - 1] + "…"

    payload: dict[str, Any] = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.system(),
        "notification": {
            "title": title,
            "body": body,
            "subtitle": brief_excerpt[:80],
        },
        "blockers": blockers,
        "delivery": {
            "method": policy.get("delivery", {}).get("method", "osascript"),
            "status": "pending",
        },
    }
    if not for_send:
        payload["delivery"]["status"] = "dry_run"
    return payload


def build_report(payload: dict[str, Any]) -> str:
    notif = payload.get("notification", {})
    lines = [
        "# Mac 本地通知计划",
        "",
        f"- 生成时间: {payload.get('generated_at')}",
        f"- 平台: {payload.get('platform')}",
        f"- 状态: {payload.get('delivery', {}).get('status')}",
        "",
        "## 通知内容",
        "",
        f"**{notif.get('title')}**",
        "",
        str(notif.get("body")),
        "",
    ]
    blockers = payload.get("blockers", [])
    if blockers:
        lines.append("## Blockers")
        lines.append("")
        for item in blockers:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def send_osascript(title: str, body: str) -> tuple[bool, str]:
    script = (
        f'display notification {json.dumps(body, ensure_ascii=False)} '
        f'with title {json.dumps(title, ensure_ascii=False)}'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if result.returncode == 0:
            return True, ""
        return False, (result.stderr or result.stdout or f"exit {result.returncode}").strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mac local notification (dry-run payload default)")
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--brief", default="reports/daily_brief.md")
    parser.add_argument("--status", default="data/repo_status.json")
    parser.add_argument("--output", default="reports/mac_notification_payload.json")
    parser.add_argument("--report", default="reports/mac_notification_plan.md")
    parser.add_argument("--write", action="store_true", help="Write payload JSON and markdown report")
    parser.add_argument("--send", action="store_true", help="Attempt osascript on macOS (skipped in CI)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    policy_path = root / args.policy
    if not policy_path.exists():
        raise SystemExit(f"Policy not found: {policy_path}")

    policy = load_yaml(policy_path)
    brief_path = root / args.brief
    status_path = root / args.status
    brief_text = brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""
    status_data = load_json(status_path) if status_path.exists() else {"repos": []}

    max_chars = int(policy.get("content", {}).get("max_body_chars", 220))
    brief_excerpt = extract_brief_excerpt(brief_text, max_chars=max_chars)
    blockers = collect_blockers(status_data)

    payload = build_payload(
        policy=policy,
        brief_excerpt=brief_excerpt,
        blockers=blockers,
        for_send=args.send,
    )

    if args.write or args.send:
        out_path = root / args.output
        report_path = root / args.report
        out_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[ok] mac notification payload: {out_path}")
        report_path.write_text(build_report(payload), encoding="utf-8")
        print(f"[ok] mac notification report: {report_path}")

    if not args.send:
        print("[dry-run] mac notification payload rendered in memory (no files, no osascript)")
        return 0

    skip, reason = should_skip_osascript(policy)
    if skip:
        payload["delivery"]["status"] = "skipped"
        payload["delivery"]["skip_reason"] = reason
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[skip] osascript skipped ({reason}); payload preserved")
        return 0

    notif = payload["notification"]
    ok, err = send_osascript(str(notif["title"]), str(notif["body"]))
    payload["delivery"]["status"] = "sent" if ok else "failed"
    if err:
        payload["delivery"]["error"] = err
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if ok:
        print("[ok] mac notification sent via osascript")
        return 0
    print(f"[warn] osascript failed: {err}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
