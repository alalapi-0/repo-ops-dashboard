#!/usr/bin/env python3
"""Build local Feishu message payload preview from daily report (no API send)."""

from __future__ import annotations

import argparse
import json
import os
import re
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


def build_payload(daily_report: str, weekly_report: str) -> dict[str, Any]:
    high = parse_high_priority_section(daily_report)
    summary_lines = high[:5] or ["暂无高优先级条目"]
    return {
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
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "本地预览载荷 — 未发送。路径已脱敏。",
                        }
                    ],
                },
            ],
        },
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "weekly_report_chars": len(weekly_report),
            "send_ready": False,
        },
    }


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
    payload = build_payload(daily_text, weekly_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] feishu payload preview: {output_path}")

    if args.send:
        webhook = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
        if not webhook:
            raise SystemExit("FEISHU_WEBHOOK_URL not set; refusing to send")
        print("[warn] --send requested but HTTP client intentionally not implemented in Round 08")
        print("[warn] Human should copy preview JSON to Feishu or add send in a future round")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
