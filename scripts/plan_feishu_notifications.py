#!/usr/bin/env python3
"""Plan Feishu/Lark daily/weekly notifications (no external API)."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

DEFAULT_POLICY = "config/feishu_notification_policy.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def dump_yaml(path: Path, data: dict[str, Any], *, header: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def source_readiness(root: Path, sources: dict[str, Any]) -> dict[str, dict[str, Any]]:
    readiness: dict[str, dict[str, Any]] = {}
    for key, rel in sources.items():
        if key.startswith("output_") or key == "payload_preview":
            continue
        path = root / str(rel)
        readiness[key] = {
            "path": str(rel),
            "exists": path.exists(),
            "bytes": path.stat().st_size if path.exists() else 0,
        }
    return readiness


def build_plan(root: Path, policy: dict[str, Any]) -> dict[str, Any]:
    sources = policy.get("sources", {})
    schedule = policy.get("schedule", {})
    channels = policy.get("channels", {})
    now = datetime.now(timezone.utc).isoformat()
    readiness = source_readiness(root, sources)

    ready_count = sum(1 for item in readiness.values() if item["exists"])
    total = len(readiness)

    return {
        "schema_version": "0.1.0",
        "generated_at": now,
        "policy_version": policy.get("policy_version", "v1"),
        "mode": "planning_only",
        "external_api_called": False,
        "summary": {
            "sources_ready": ready_count,
            "sources_total": total,
            "daily_enabled": schedule.get("daily", {}).get("enabled", False),
            "weekly_enabled": schedule.get("weekly", {}).get("enabled", False),
            "feishu_mode": channels.get("feishu_bot", {}).get("mode", "preview_only"),
            "hitl_review_id": channels.get("feishu_bot", {}).get("hitl_review_id"),
        },
        "schedule": schedule,
        "source_readiness": readiness,
        "next_steps": [
            "HumanOwner 审阅 review_queue 中 feishu 日报权限项",
            "配置 FEISHU_WEBHOOK_URL 后使用 send_feishu_notification.py --send",
            "refresh_status.sh 默认仅生成预览，不加 --feishu-send",
        ],
    }


def build_report(plan: dict[str, Any]) -> str:
    summary = plan.get("summary", {})
    schedule = plan.get("schedule", {})
    daily = schedule.get("daily", {})
    weekly = schedule.get("weekly", {})
    lines = [
        "# Feishu/Lark 通知规划报告",
        "",
        f"- 生成时间: {plan.get('generated_at')}",
        f"- 模式: {plan.get('mode')}（未调用外部 API）",
        f"- 来源就绪: {summary.get('sources_ready')}/{summary.get('sources_total')}",
        "",
        "## 排期建议",
        "",
        f"- **日报**: cron `{daily.get('suggested_cron')}` · {daily.get('card_title')}",
        f"- **周报**: cron `{weekly.get('suggested_cron')}` · {weekly.get('card_title')}",
        "",
        "## 来源文件状态",
        "",
    ]
    for key, item in plan.get("source_readiness", {}).items():
        status = "✓" if item.get("exists") else "✗"
        lines.append(f"- {status} `{item.get('path')}` ({item.get('bytes', 0)} bytes)")
    lines.extend(
        [
            "",
            "## 下一步",
            "",
        ]
    )
    for step in plan.get("next_steps", []):
        lines.append(f"- {step}")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan Feishu notifications without API calls")
    parser.add_argument("--policy", default=DEFAULT_POLICY, help="Policy YAML path")
    parser.add_argument("--write", action="store_true", help="Write plan YAML and markdown report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    policy_path = root / args.policy
    if not policy_path.exists():
        raise SystemExit(f"Policy not found: {policy_path}")

    policy = load_yaml(policy_path)
    plan = build_plan(root, policy)
    sources = policy.get("sources", {})
    out_yaml = root / sources.get("output_plan", "governance/feishu_notification_plan.yaml")
    out_md = root / sources.get("output_report", "reports/feishu_notification_planning.md")

    summary = plan["summary"]
    print(
        f"[plan] feishu notification planning: "
        f"sources={summary['sources_ready']}/{summary['sources_total']} "
        f"daily={summary['daily_enabled']} weekly={summary['weekly_enabled']} "
        f"mode={summary['feishu_mode']}"
    )

    if args.write:
        dump_yaml(
            out_yaml,
            plan,
            header="# Feishu notification plan (planning only, no API).\n",
        )
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(build_report(plan), encoding="utf-8")
        print(f"[ok] plan yaml: {out_yaml}")
        print(f"[ok] plan report: {out_md}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
