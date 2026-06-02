#!/usr/bin/env python3
"""Generate weekly_digest Markdown from governance state and reports (rule-based, no external API)."""

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

OPEN_REVIEW_STATUSES = {"open", "pending", "awaiting_human"}
DEFAULT_TEMPLATE = "prompts/weekly_digest.md"
DEFAULT_OUTPUT = "governance/digests/weekly/weekly_digest.md"


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


def summarize_portfolio(portfolio: dict[str, Any]) -> str:
    summary = portfolio.get("summary", {})
    if not summary:
        return "- portfolio_state 未找到"
    return "\n".join(
        [
            f"- 项目总数：{summary.get('total_projects', '—')}",
            f"- 活跃：{summary.get('active_projects', '—')}",
            f"- 阻塞：{summary.get('blocked_projects', '—')}",
            f"- review_queue 待决：{summary.get('review_queue_open', '—')}",
        ]
    )


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


def summarize_active_tasks(task_queue: dict[str, Any]) -> str:
    tasks = [t for t in task_queue.get("tasks", []) if t.get("is_active")]
    if not tasks:
        return "- 无活跃治理任务"
    return "\n".join(
        f"- **{t.get('task_id')}**（{t.get('assigned_agent', '—')}）— {t.get('title', '')}"
        for t in tasks[:5]
    )


def summarize_priority_top(status: dict[str, Any], limit: int = 5) -> str:
    repos = list(status.get("repos", []))
    ranked = sorted(
        repos,
        key=lambda r: (
            {"high": 0, "medium": 1, "low": 2}.get(str(r.get("priority", "low")), 9),
            -int(r.get("health_score", 0)),
            str(r.get("name", "")),
        ),
    )
    lines: list[str] = []
    for idx, repo in enumerate(ranked[:limit], start=1):
        name = repo.get("name", "unknown")
        priority = repo.get("priority", "—")
        agent = repo.get("recommended_agent", "—")
        lines.append(f"{idx}. **{name}**（{priority} / {agent}）")
    return "\n".join(lines) if lines else "1. 暂无数据"


def format_human_notes(notes: dict[str, Any]) -> str:
    if not notes:
        return "- 无（可编辑 data/human_notes.json）"
    lines = [f"- 周次：{notes.get('week_label', '—')}"]
    for item in notes.get("notes", []):
        lines.append(f"- {item}")
    focus = notes.get("focus_repos", [])
    if focus:
        lines.append(f"- 关注仓库：{', '.join(str(x) for x in focus)}")
    return "\n".join(lines)


def build_week_summary(status: dict[str, Any], portfolio: dict[str, Any]) -> str:
    repo_count = len(status.get("repos", []))
    ps = portfolio.get("summary", {})
    return "\n".join(
        [
            f"- 扫描仓库：{repo_count}",
            f"- 活跃项目：{ps.get('active_projects', '—')}",
            f"- 阻塞项目：{ps.get('blocked_projects', '—')}",
            f"- 治理轮次：{portfolio.get('current_round') or '见 round_state'}",
        ]
    )


def build_short_reminder(
    *,
    top_names: list[str],
    review_open_count: int,
    active_task_count: int,
) -> str:
    names = ", ".join(top_names[:2]) or "无"
    text = (
        f"本周关注：{names}。"
        f"review_queue 待决 {review_open_count} 项；活跃治理任务 {active_task_count} 项。"
        "HumanOwner 优先处理 HITL 决策。"
    )
    return text[:200]


def render_digest(
    template: str,
    *,
    status: dict[str, Any],
    portfolio: dict[str, Any],
    review_queue: dict[str, Any],
    task_queue: dict[str, Any],
    round_state: dict[str, Any],
    human_notes: dict[str, Any],
) -> str:
    open_items = [
        item
        for item in review_queue.get("items", [])
        if str(item.get("status", "")).lower() in OPEN_REVIEW_STATUSES
    ]
    active_tasks = [t for t in task_queue.get("tasks", []) if t.get("is_active")]
    repos = list(status.get("repos", []))
    ranked = sorted(
        repos,
        key=lambda r: (
            {"high": 0, "medium": 1, "low": 2}.get(str(r.get("priority", "low")), 9),
            -int(r.get("health_score", 0)),
        ),
    )
    top_names = [str(r.get("name", "")) for r in ranked[:3] if r.get("name")]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    replacements = {
        "{{generated_at}}": generated_at,
        "{{week_summary}}": build_week_summary(status, portfolio),
        "{{portfolio_summary}}": summarize_portfolio(portfolio),
        "{{priority_top}}": summarize_priority_top(status),
        "{{review_queue_open}}": summarize_review_queue_open(review_queue),
        "{{active_tasks}}": summarize_active_tasks(task_queue),
        "{{current_round}}": str(round_state.get("current_round", "—")),
        "{{round_status}}": str(round_state.get("status", "—")),
        "{{next_round}}": str(round_state.get("next_round", "—")),
        "{{human_notes}}": format_human_notes(human_notes),
        "{{short_reminder}}": build_short_reminder(
            top_names=top_names,
            review_open_count=len(open_items),
            active_task_count=len(active_tasks),
        ),
    }
    text = template
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate weekly_digest markdown")
    parser.add_argument("--input", default="data/repo_status.json", help="Repo status JSON")
    parser.add_argument("--portfolio", default="governance/portfolio_state.yaml")
    parser.add_argument("--review-queue", default="governance/review_queue.yaml")
    parser.add_argument("--task-queue", default="governance/governance_task_queue.yaml")
    parser.add_argument("--round-state", default="round_state/current_round.yaml")
    parser.add_argument("--human-notes", default="data/human_notes.json")
    parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status_path = Path(args.input)
    if not status_path.exists():
        raise SystemExit(f"Input not found: {status_path}")

    status = load_json(status_path)
    portfolio = load_yaml(Path(args.portfolio))
    review_queue = load_yaml(Path(args.review_queue))
    task_queue = load_yaml(Path(args.task_queue))
    round_state = load_yaml(Path(args.round_state))
    human_notes = load_json(Path(args.human_notes))
    template = load_text(Path(args.template))

    digest = render_digest(
        template,
        status=status,
        portfolio=portfolio,
        review_queue=review_queue,
        task_queue=task_queue,
        round_state=round_state,
        human_notes=human_notes,
    )

    print(f"[ok] weekly digest: repos={len(status.get('repos', []))}")

    if args.dry_run:
        print("[dry-run] file not written")
        return 0

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(digest, encoding="utf-8")
    print(f"[ok] weekly digest -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
