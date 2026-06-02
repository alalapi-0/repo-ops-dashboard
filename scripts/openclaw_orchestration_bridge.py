#!/usr/bin/env python3
"""OpenClaw orchestration bridge — read governance state, dry-run triggers, generate reminders."""

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

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
OPEN_REVIEW_STATUSES = {"open", "pending", "awaiting_human"}
DEFAULT_MANIFEST = "governance/openclaw_orchestration.manifest.yaml"
DEFAULT_TEMPLATE = "prompts/openclaw_orchestration_brief.md"
DEFAULT_BRIEF = "reports/openclaw_orchestration_brief.md"
DEFAULT_SNAPSHOT = "governance/digests/daily/openclaw_orchestration.snapshot.yaml"

DEFAULT_DRY_RUN_COMMANDS = [
    "python3 scripts/agent_gate.py",
    "python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run",
    "python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json",
    "python3 scripts/generate_report.py --input data/repo_status.example.json",
]


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


def pick_top_projects(projects: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    def key(row: dict[str, Any]) -> tuple[int, str]:
        lifecycle = str(row.get("lifecycle", ""))
        if lifecycle in {"archived", "frozen", "freeze_candidate"}:
            return (99, str(row.get("project_id", "")))
        pr = PRIORITY_RANK.get(str(row.get("priority", "low")), 9)
        return (pr, str(row.get("project_id", "")))

    candidates = [
        p
        for p in sorted(projects, key=key)
        if str(p.get("lifecycle", "")) not in {"archived", "frozen"}
    ]
    return candidates[:limit]


def pick_defer_projects(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in projects:
        lifecycle = str(row.get("lifecycle", ""))
        if lifecycle in {"freeze_candidate", "archived", "frozen"}:
            out.append(row)
            continue
        if str(row.get("health", "")) == "red" and str(row.get("priority", "")) == "low":
            out.append(row)
    return out


def format_project_line(row: dict[str, Any], index: int | None = None) -> str:
    pid = row.get("project_id", "unknown")
    repo = row.get("repo_name", pid)
    agent = row.get("recommended_agent", "Human")
    blockers = row.get("blockers") or []
    actions = row.get("next_actions") or []
    prefix = f"{index}. " if index is not None else "- "
    blocker_text = "; ".join(str(b) for b in blockers) if blockers else "无卡点"
    action = actions[0] if actions else "继续治理推进"
    return f"{prefix}**{repo}**（{agent}）— {action}；卡点：{blocker_text}"


def summarize_portfolio(portfolio: dict[str, Any]) -> str:
    summary = portfolio.get("summary", {})
    if not summary:
        return "- portfolio_state 未找到或为空"
    lines = [
        f"- 项目总数：{summary.get('total_projects', '—')}",
        f"- 活跃：{summary.get('active_projects', '—')}",
        f"- 阻塞：{summary.get('blocked_projects', '—')}",
        f"- review_queue 待决：{summary.get('review_queue_open', '—')}",
        f"- budget_warning：{summary.get('budget_warning', False)}",
    ]
    return "\n".join(lines)


def summarize_review_queue_open(review_queue: dict[str, Any]) -> str:
    items = list(review_queue.get("items", []))
    open_items = [
        item
        for item in items
        if str(item.get("status", "")).lower() in OPEN_REVIEW_STATUSES
    ]
    if not open_items:
        return "- 无待决 review item"
    lines: list[str] = []
    for item in open_items[:5]:
        rid = item.get("review_id", "unknown")
        kind = item.get("decision_type", item.get("type", "—"))
        prompt = str(item.get("prompt", ""))[:80]
        lines.append(f"- **{rid}**（{kind}）：{prompt}")
    if len(open_items) > 5:
        lines.append(f"- … 另有 {len(open_items) - 5} 项待决")
    return "\n".join(lines)


def summarize_active_tasks(task_queue: dict[str, Any]) -> str:
    tasks = [t for t in task_queue.get("tasks", []) if t.get("is_active")]
    if not tasks:
        return "- 无活跃治理任务"
    lines: list[str] = []
    for task in tasks[:5]:
        lines.append(
            f"- **{task.get('task_id')}**（{task.get('assigned_agent', '—')}）— {task.get('title', '')}"
        )
    return "\n".join(lines)


def build_short_reminder(
    *,
    top: list[dict[str, Any]],
    defer: list[dict[str, Any]],
    review_open_count: int,
    current_round: str,
) -> str:
    names = ", ".join(str(p.get("repo_name") or p.get("project_id")) for p in top[:2]) or "无"
    text = (
        f"Round {current_round or '—'}：优先 {names}。"
        f"暂缓 {len(defer)} 项；review_queue 待决 {review_open_count} 项。"
        "OpenClaw 只读编排，编程交给 Cursor/Codex。"
    )
    return text[:200]


def build_snapshot(
    *,
    portfolio: dict[str, Any],
    review_queue: dict[str, Any],
    task_queue: dict[str, Any],
    round_state: dict[str, Any],
    manifest: dict[str, Any],
    reminder: str,
) -> dict[str, Any]:
    open_items = [
        item
        for item in review_queue.get("items", [])
        if str(item.get("status", "")).lower() in OPEN_REVIEW_STATUSES
    ]
    return {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "role": manifest.get("role", "orchestration_entry"),
        "current_round": round_state.get("current_round"),
        "round_status": round_state.get("status"),
        "next_round": round_state.get("next_round"),
        "portfolio_summary": portfolio.get("summary", {}),
        "review_queue_open_count": len(open_items),
        "review_queue_open_ids": [item.get("review_id") for item in open_items[:10]],
        "active_task_ids": [t.get("task_id") for t in task_queue.get("tasks", []) if t.get("is_active")],
        "top_project_ids": [p.get("project_id") for p in pick_top_projects(list(portfolio.get("projects", [])))],
        "short_reminder": reminder,
        "dry_run_only": True,
        "external_api_called": False,
    }


def render_brief(
    template: str,
    *,
    portfolio: dict[str, Any],
    review_queue: dict[str, Any],
    task_queue: dict[str, Any],
    round_state: dict[str, Any],
    dry_run_commands: list[str],
) -> str:
    projects = list(portfolio.get("projects", []))
    top = pick_top_projects(projects)
    defer = pick_defer_projects(projects)
    open_items = [
        item
        for item in review_queue.get("items", [])
        if str(item.get("status", "")).lower() in OPEN_REVIEW_STATUSES
    ]
    current_round = str(round_state.get("current_round", "—"))
    reminder = build_short_reminder(
        top=top,
        defer=defer,
        review_open_count=len(open_items),
        current_round=current_round,
    )
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    replacements = {
        "{{generated_at}}": generated_at,
        "{{current_round}}": current_round,
        "{{round_status}}": str(round_state.get("status", "—")),
        "{{next_round}}": str(round_state.get("next_round", "—")),
        "{{portfolio_summary}}": summarize_portfolio(portfolio),
        "{{review_queue_open}}": summarize_review_queue_open(review_queue),
        "{{active_tasks}}": summarize_active_tasks(task_queue),
        "{{top_projects}}": "\n".join(format_project_line(p, i + 1) for i, p in enumerate(top))
        or "1. 暂无高优先级可推进项目",
        "{{defer_projects}}": "\n".join(format_project_line(p) for p in defer) or "- 无",
        "{{dry_run_commands}}": "\n".join(dry_run_commands),
        "{{short_reminder}}": reminder,
    }
    text = template
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenClaw orchestration bridge (read-only, dry-run default)")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    parser.add_argument("--portfolio", default="governance/portfolio_state.yaml")
    parser.add_argument("--review-queue", default="governance/review_queue.yaml")
    parser.add_argument("--task-queue", default="governance/governance_task_queue.yaml")
    parser.add_argument("--round-state", default="round_state/current_round.yaml")
    parser.add_argument("--output", default=DEFAULT_BRIEF)
    parser.add_argument("--snapshot", default=DEFAULT_SNAPSHOT)
    parser.add_argument("--dry-run", action="store_true", help="Print summary only; do not write files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_yaml(Path(args.manifest))
    portfolio = load_yaml(Path(args.portfolio))
    review_queue = load_yaml(Path(args.review_queue))
    task_queue = load_yaml(Path(args.task_queue))
    round_state = load_yaml(Path(args.round_state))
    template = load_text(Path(args.template))

    dry_run_commands = list(manifest.get("dry_run_triggers") or DEFAULT_DRY_RUN_COMMANDS)
    brief = render_brief(
        template,
        portfolio=portfolio,
        review_queue=review_queue,
        task_queue=task_queue,
        round_state=round_state,
        dry_run_commands=dry_run_commands,
    )
    projects = list(portfolio.get("projects", []))
    open_items = [
        item
        for item in review_queue.get("items", [])
        if str(item.get("status", "")).lower() in OPEN_REVIEW_STATUSES
    ]
    reminder = build_short_reminder(
        top=pick_top_projects(projects),
        defer=pick_defer_projects(projects),
        review_open_count=len(open_items),
        current_round=str(round_state.get("current_round", "")),
    )
    snapshot = build_snapshot(
        portfolio=portfolio,
        review_queue=review_queue,
        task_queue=task_queue,
        round_state=round_state,
        manifest=manifest,
        reminder=reminder,
    )

    print(
        f"[ok] openclaw bridge: round={round_state.get('current_round', '—')} "
        f"review_open={len(open_items)} active_tasks="
        f"{sum(1 for t in task_queue.get('tasks', []) if t.get('is_active'))}"
    )

    if args.dry_run:
        print("[dry-run] brief and snapshot not written")
        return 0

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(brief, encoding="utf-8")
    print(f"[ok] brief -> {output_path}")

    snapshot_path = Path(args.snapshot)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(yaml.safe_dump(snapshot, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"[ok] snapshot -> {snapshot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
