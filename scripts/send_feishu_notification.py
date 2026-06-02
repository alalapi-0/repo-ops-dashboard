#!/usr/bin/env python3
"""Send Feishu/Lark bot notification (dry-run mock outbound by default)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_feishu_payload import (  # noqa: E402
    build_payload,
    compute_status_stats,
    extract_brief_excerpt,
    feishu_error_hint,
    load_json,
    load_text,
    send_webhook,
    truncate_for_feishu,
    webhook_body,
)

DEFAULT_OUTBOUND = "reports/feishu_outbound_preview.json"
DEFAULT_PREVIEW = "reports/feishu_payload_preview.json"


def card_title_for_mode(mode: str, policy: dict[str, Any] | None) -> str:
    schedule = (policy or {}).get("schedule", {})
    section = schedule.get(mode, {})
    return str(section.get("card_title") or ("Repo Ops 周报摘要" if mode == "weekly" else "Repo Ops 日报摘要"))


def apply_card_title(payload: dict[str, Any], title: str) -> dict[str, Any]:
    updated = json.loads(json.dumps(payload))
    card = updated.setdefault("card", {})
    header = card.setdefault("header", {})
    header["title"] = {"tag": "plain_text", "content": title}
    return updated


def build_outbound_record(
    *,
    mode: str,
    payload: dict[str, Any],
    webhook_configured: bool,
    send_attempted: bool,
    http_status: int | None = None,
    response_excerpt: str = "",
    error: str = "",
) -> dict[str, Any]:
    body = truncate_for_feishu(webhook_body(payload))
    if send_attempted and http_status and http_status < 400 and not error:
        delivery_status = "sent"
    elif send_attempted and (error or (http_status and http_status >= 400)):
        delivery_status = "failed"
    elif send_attempted and not webhook_configured:
        delivery_status = "mock"
    elif not send_attempted:
        delivery_status = "preview"
    else:
        delivery_status = "failed"

    return {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "channel": "feishu_bot",
        "mode": mode,
        "delivery": {
            "status": delivery_status,
            "webhook_configured": webhook_configured,
            "send_attempted": send_attempted,
            "http_status": http_status,
            "response_excerpt": response_excerpt[:500],
            "error": error,
        },
        "payload_bytes": len(json.dumps(body, ensure_ascii=False).encode("utf-8")),
        "outbound_body": body,
    }


def run_prepare_payload(
    *,
    daily: Path,
    weekly: Path,
    status: Path,
    brief: Path,
    llm_summary: Path,
    preview_out: Path,
    mode: str,
    policy: dict[str, Any] | None,
) -> dict[str, Any]:
    daily_text = load_text(daily)
    weekly_text = load_text(weekly) if weekly.exists() else ""
    stats = compute_status_stats(load_json(status)) if status.exists() else None
    brief_text = load_text(brief) if brief.exists() else ""
    brief_excerpt = extract_brief_excerpt(brief_text)
    llm_text = load_text(llm_summary) if llm_summary.exists() else ""
    llm_excerpt = extract_brief_excerpt(llm_text, max_chars=400) if llm_text.strip() else ""

    if mode == "weekly" and weekly_text.strip():
        brief_excerpt = extract_brief_excerpt(weekly_text, max_chars=600)

    payload = build_payload(
        daily_text,
        weekly_text,
        stats=stats,
        brief_excerpt=brief_excerpt,
        llm_excerpt=llm_excerpt,
        for_send=False,
    )
    payload = apply_card_title(payload, card_title_for_mode(mode, policy))

    preview_out.parent.mkdir(parents=True, exist_ok=True)
    preview_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Feishu notification MVP (dry-run outbound preview default)")
    parser.add_argument("--mode", choices=("daily", "weekly"), default="daily", help="Notification cadence")
    parser.add_argument("--daily", default="reports/daily_repo_report.md")
    parser.add_argument("--weekly", default="reports/weekly_repo_report.md")
    parser.add_argument("--status", default="data/repo_status.json")
    parser.add_argument("--brief", default="reports/daily_brief.md")
    parser.add_argument("--llm-summary", default="reports/llm_daily_summary.md")
    parser.add_argument("--preview-output", default=DEFAULT_PREVIEW)
    parser.add_argument("--outbound-output", default=DEFAULT_OUTBOUND)
    parser.add_argument(
        "--send",
        action="store_true",
        help="Opt-in send when FEISHU_WEBHOOK_URL is set; otherwise mock outbound preview",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    policy_path = ROOT / "config" / "feishu_notification_policy.yaml"
    policy: dict[str, Any] | None = None
    if policy_path.exists():
        try:
            import yaml

            with policy_path.open("r", encoding="utf-8") as handle:
                policy = yaml.safe_load(handle) or {}
        except ImportError:
            policy = None

    daily = ROOT / args.daily
    if not daily.exists():
        raise SystemExit(f"Daily report not found: {daily}")

    payload = run_prepare_payload(
        daily=daily,
        weekly=ROOT / args.weekly,
        status=ROOT / args.status,
        brief=ROOT / args.brief,
        llm_summary=ROOT / args.llm_summary,
        preview_out=ROOT / args.preview_output,
        mode=args.mode,
        policy=policy,
    )
    print(f"[ok] feishu payload preview: {args.preview_output}")

    webhook = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
    outbound_path = ROOT / args.outbound_output
    outbound_path.parent.mkdir(parents=True, exist_ok=True)

    if args.send and webhook:
        status_code, response_text = send_webhook(webhook, payload)
        error = ""
        try:
            parsed = json.loads(response_text)
            code = parsed.get("code", parsed.get("StatusCode"))
            if code not in (0, None) and str(code) != "0":
                hint = feishu_error_hint(code)
                error = f"feishu code={code} {parsed.get('msg', '')} {hint}".strip()
        except json.JSONDecodeError:
            if status_code >= 400:
                error = f"http {status_code}"
        record = build_outbound_record(
            mode=args.mode,
            payload=payload,
            webhook_configured=True,
            send_attempted=True,
            http_status=status_code,
            response_excerpt=response_text,
            error=error,
        )
        outbound_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[send] http_status={status_code}")
        print(f"[ok] outbound record: {outbound_path}")
        if error or status_code >= 400:
            return 2
        print("[ok] feishu message sent (webhook URL not logged)")
        return 0

    record = build_outbound_record(
        mode=args.mode,
        payload=payload,
        webhook_configured=bool(webhook),
        send_attempted=False,
    )
    outbound_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.send and not webhook:
        print("[mock] FEISHU_WEBHOOK_URL not set; wrote outbound preview (no send)")
    else:
        print(f"[dry-run] outbound preview: {outbound_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
