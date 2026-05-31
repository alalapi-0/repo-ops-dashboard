#!/usr/bin/env python3
"""Build local Feishu message payload preview from daily report; optional webhook send."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import base64
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def redact_paths(text: str) -> str:
    return re.sub(r"/Users/[^\s|]+/", "[local-path]/", text)


def parse_high_priority_section(report: str) -> list[str]:
    lines = report.splitlines()
    items: list[str] = []
    in_section = False
    for line in lines:
        if line.startswith("## 高优先级仓库"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("- **"):
            items.append(redact_paths(line.lstrip("- ").strip()))
    return items


def build_payload(daily_report: str, weekly_report: str, *, for_send: bool) -> dict[str, Any]:
    high = parse_high_priority_section(daily_report)
    summary_lines = high[:5] or ["暂无高优先级条目"]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    note = (
        f"Repo Ops · {generated_at} · 路径已脱敏"
        if for_send
        else "本地预览载荷 — 未发送。路径已脱敏。"
    )
    body: dict[str, Any] = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "Repo Ops 日报摘要"},
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "\n".join(f"- {item}" for item in summary_lines),
                    },
                },
                {
                    "tag": "note",
                    "elements": [{"tag": "plain_text", "content": note}],
                },
            ],
        },
    }
    if not for_send:
        body["meta"] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "weekly_report_chars": len(weekly_report),
            "send_ready": True,
        }
    return body


def webhook_body(payload: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in payload.items() if k != "meta"}


def sign_payload(secret: str, timestamp: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    digest = hmac.new(string_to_sign.encode("utf-8"), b"", hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def send_webhook(webhook_url: str, payload: dict[str, Any]) -> tuple[int, str]:
    body = webhook_body(payload)
    sign_secret = os.environ.get("FEISHU_SIGN_SECRET", "").strip()
    if sign_secret:
        timestamp = str(int(time.time()))
        body["timestamp"] = timestamp
        body["sign"] = sign_payload(sign_secret, timestamp)

    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return response.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return exc.code, raw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare Feishu payload preview locally")
    parser.add_argument("--daily", default="reports/daily_repo_report.md", help="Daily report path")
    parser.add_argument("--weekly", default="reports/weekly_repo_report.md", help="Weekly report path")
    parser.add_argument(
        "--output",
        default="reports/feishu_payload_preview.json",
        help="Output preview JSON path",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Opt-in send (requires FEISHU_WEBHOOK_URL env, never committed)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    daily_path = Path(args.daily)
    weekly_path = Path(args.weekly)
    output_path = Path(args.output)

    if not daily_path.exists():
        raise SystemExit(f"Daily report not found: {daily_path}")

    daily_text = load_text(daily_path)
    weekly_text = load_text(weekly_path) if weekly_path.exists() else ""
    payload = build_payload(daily_text, weekly_text, for_send=args.send)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] feishu payload preview: {output_path}")

    if not args.send:
        return 0

    webhook = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
    if not webhook:
        raise SystemExit("FEISHU_WEBHOOK_URL not set; refusing to send")

    status, response_text = send_webhook(webhook, payload)
    print(f"[send] http_status={status}")
    if response_text:
        print(f"[send] body={response_text[:500]}")
    try:
        parsed = json.loads(response_text)
        code = parsed.get("code", parsed.get("StatusCode"))
        if code not in (0, None) and str(code) != "0":
            print(f"[error] feishu api code={code} msg={parsed.get('msg', parsed.get('StatusMessage', ''))}")
            return 2
    except json.JSONDecodeError:
        if status >= 400:
            return 2
    if status >= 400:
        return 2
    print("[ok] feishu message sent (webhook URL not logged)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
