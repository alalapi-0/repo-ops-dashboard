#!/usr/bin/env python3
"""Generate governance daily briefing from repo status and review_queue (rule-based, no external API)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

import generate_daily_brief as daily_brief  # noqa: E402

OPEN_REVIEW_STATUSES = {"open", "pending", "awaiting_human"}
DEFAULT_TEMPLATE = "prompts/daily_briefing.md"
DEFAULT_OUTPUT = "governance/digests/daily/daily_briefing.md"
DEFAULT_REPORT_OUTPUT = "reports/daily_briefing.md"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else {}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def summarize_review_queue_open(review_queue: dict[str, Any]) -> str:
    open_items = [
        item
        for item in review_queue.get("items", [])
        if str(item.get("status", "")).lower() in OPEN_REVIEW_STATUSES
    ]
    if not open_items:
        return "- 无待决 review item"
    return "\n".join(
        f"- **{item.get('review_id', 'unknown')}**：{str(item.get('prompt', ''))[:100]}"
        for item in open_items[:5]
    )


def build_short_reminder(
    *,
    top: list[dict[str, Any]],
    defer: list[dict[str, Any]],
    review_open_count: int,
    current_round: str,
) -> str:
    names = ", ".join(str(r.get("name")) for r in top[:2]) or "无"
    text = (
        f"Round {current_round or '—'}：今日优先 {names}。"
        f"暂缓 {len(defer)} 仓；review_queue 待决 {review_open_count} 项。"
        "编程交给 Cursor/Codex，决策留给 HumanOwner。"
    )
    return text[:200]


def render_briefing(
    template: str,
    *,
    status: dict[str, Any],
    review_queue: dict[str, Any],
    round_state: dict[str, Any],
) -> str:
    repos = list(status.get("repos", []))
    top = daily_brief.pick_top_push(repos)
    defer = daily_brief.pick_defer(repos)
    open_items = [
        item
        for item in review_queue.get("items", [])
        if str(item.get("status", "")).lower() in OPEN_REVIEW_STATUSES
    ]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    current_round = str(round_state.get("current_round", "—"))
    replacements = {
        "{{generated_at}}": generated_at,
        "{{current_round}}": current_round,
        "{{round_status}}": str(round_state.get("status", "—")),
        "{{next_round}}": str(round_state.get("next_round", "—")),
        "{{top_repos}}": "\n".join(daily_brief.format_repo_line(r, i + 1) for i, r in enumerate(top))
        or "1. 暂无高优先级可推进仓",
        "{{defer_repos}}": "\n".join(daily_brief.format_repo_line(r) for r in defer) or "- 无",
        "{{review_queue_open}}": summarize_review_queue_open(review_queue),
        "{{risk_notes}}": daily_brief.build_risk_notes(repos),
        "{{cursor_codex_drafts}}": daily_brief.build_cursor_codex_drafts(top),
        "{{short_reminder}}": build_short_reminder(
            top=top,
            defer=defer,
            review_open_count=len(open_items),
            current_round=current_round,
        ),
    }
    text = template
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate governance daily briefing markdown")
    parser.add_argument("--input", default="data/repo_status.json", help="Repo status JSON")
    parser.add_argument("--review-queue", default="governance/review_queue.yaml")
    parser.add_argument("--round-state", default="round_state/current_round.yaml")
    parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--report-output", default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status_path = Path(args.input)
    if not status_path.exists():
        raise SystemExit(f"Input not found: {status_path}")

    status = load_json(status_path)
    review_queue = load_yaml(Path(args.review_queue))
    round_state = load_yaml(Path(args.round_state))
    template = load_text(Path(args.template))
    briefing = render_briefing(
        template,
        status=status,
        review_queue=review_queue,
        round_state=round_state,
    )

    print(f"[ok] daily briefing: repos={len(status.get('repos', []))}")

    if args.dry_run:
        print("[dry-run] files not written")
        return 0

    for output in (Path(args.output), Path(args.report_output)):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(briefing, encoding="utf-8")
        print(f"[ok] daily briefing -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
