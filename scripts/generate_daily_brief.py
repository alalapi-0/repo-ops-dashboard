#!/usr/bin/env python3
"""Generate daily briefing from repo status (rule-based, no external API)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sort_for_push(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(repo: dict[str, Any]) -> tuple[int, int, str]:
        if repo.get("archive_candidate") or repo.get("freeze_candidate"):
            return (99, 100, str(repo.get("name", "")))
        pr = PRIORITY_RANK.get(str(repo.get("priority", "low")), 9)
        health = -int(repo.get("health_score", 0))
        return (pr, health, str(repo.get("name", "")))

    return sorted(repos, key=key)


def pick_top_push(repos: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    candidates = [
        r
        for r in sort_for_push(repos)
        if not r.get("archive_candidate")
        and str(r.get("status", "")) not in {"missing", "empty"}
    ]
    return candidates[:limit]


def pick_defer(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for repo in repos:
        if repo.get("archive_candidate") or repo.get("freeze_candidate"):
            out.append(repo)
            continue
        if str(repo.get("priority", "")) == "low" and int(repo.get("health_score", 0)) < 30:
            out.append(repo)
    return out


def format_repo_line(repo: dict[str, Any], index: int | None = None) -> str:
    name = repo.get("name", "unknown")
    agent = repo.get("recommended_agent", "Cursor")
    blockers = repo.get("blockers") or []
    next_actions = repo.get("next_actions") or []
    prefix = f"{index}. " if index is not None else "- "
    blocker_text = "; ".join(blockers) if blockers else "无卡点"
    action = next_actions[0] if next_actions else "继续下一轮"
    return f"{prefix}**{name}**（{agent}）— {action}；卡点：{blocker_text}"


def build_cursor_codex_drafts(top: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for repo in top:
        agent = str(repo.get("recommended_agent", "Cursor"))
        name = repo.get("name", "unknown")
        blockers = "; ".join(repo.get("blockers") or ["无"])
        lines.append(f"- **{name}** → {agent}：{blockers}")
    return "\n".join(lines) if lines else "- 暂无"


def build_risk_notes(repos: list[dict[str, Any]]) -> str:
    blocked = [r.get("name") for r in repos if r.get("blockers")]
    archived = [r.get("name") for r in repos if r.get("archive_candidate")]
    notes: list[str] = []
    if blocked:
        notes.append(f"有卡点仓库 {len(blocked)} 个：{', '.join(str(x) for x in blocked[:5])}")
    if archived:
        notes.append(f"归档候选：{', '.join(str(x) for x in archived)}")
    if not notes:
        notes.append("无额外风险；按 priority 推进即可。")
    return "\n".join(f"- {n}" for n in notes)


def short_reminder(top: list[dict[str, Any]], defer: list[dict[str, Any]]) -> str:
    names = ", ".join(str(r.get("name")) for r in top[:2]) or "无"
    defer_count = len(defer)
    text = (
        f"今日优先推进：{names}。暂缓 {defer_count} 仓勿动。"
        "编排交给 Cursor Automations，编程交给 Cursor/Codex。"
    )
    return text[:200]


def render_brief(
    template: str,
    status: dict[str, Any],
) -> str:
    repos = list(status.get("repos", []))
    top = pick_top_push(repos)
    defer = pick_defer(repos)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    top_text = "\n".join(format_repo_line(r, i + 1) for i, r in enumerate(top)) or "1. 暂无高优先级可推进仓"
    defer_text = "\n".join(format_repo_line(r) for r in defer) or "- 无"
    risk = build_risk_notes(repos)
    drafts = build_cursor_codex_drafts(top)
    reminder = short_reminder(top, defer)

    text = template
    replacements = {
        "{{generated_at}}": generated_at,
        "{{top_repos}}": top_text,
        "{{defer_repos}}": defer_text,
        "{{risk_notes}}": risk,
        "{{cursor_codex_drafts}}": drafts,
        "{{short_reminder}}": reminder,
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate daily brief")
    parser.add_argument("--input", default="data/repo_status.json", help="Repo status JSON")
    parser.add_argument("--template", default="prompts/daily_brief.md", help="Brief template")
    parser.add_argument("--output", default="reports/daily_brief.md", help="Output markdown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    status = load_json(input_path)
    template = load_text(Path(args.template))
    brief = render_brief(template, status)

    if "{{short_reminder}}" not in template:
        brief += f"\n\n## 短提醒\n\n{short_reminder(pick_top_push(list(status.get('repos', []))), pick_defer(list(status.get('repos', []))))}\n"

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(brief, encoding="utf-8")
    print(f"[ok] daily brief -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
