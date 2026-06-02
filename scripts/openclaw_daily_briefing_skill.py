#!/usr/bin/env python3
"""OpenClaw daily briefing skill — read repo_status + digests, emit skill snapshot (dry-run default)."""

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
DEFAULT_TEMPLATE = "prompts/openclaw_daily_briefing_skill.md"
DEFAULT_BRIEF = "reports/openclaw_daily_briefing_skill.md"
DEFAULT_SNAPSHOT = "governance/digests/daily/openclaw_daily_briefing.snapshot.yaml"
DEFAULT_MANIFEST = "governance/openclaw_orchestration.manifest.yaml"

DEFAULT_DRY_RUN_COMMANDS = [
    "python3 scripts/agent_gate.py",
    "python3 scripts/openclaw_daily_briefing_skill.py --dry-run",
    "python3 scripts/openclaw_orchestration_bridge.py --dry-run",
    "python3 scripts/generate_daily_briefing.py --input data/repo_status.example.json --dry-run",
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


def excerpt_markdown(path: Path, *, max_lines: int = 12) -> str:
    if not path.exists():
        return f"- 未找到：{path.as_posix()}"
    lines = [ln.rstrip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        return "- 文件为空"
    picked = lines[:max_lines]
    if len(lines) > max_lines:
        picked.append(f"- … 另有 {len(lines) - max_lines} 行")
    return "\n".join(f"- {ln.lstrip('- ').strip()}" if not ln.startswith("-") else ln for ln in picked)


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
        f"Round {current_round or '—'}：优先 {names}。"
        f"暂缓 {len(defer)} 仓；review_queue 待决 {review_open_count} 项。"
        "OpenClaw 只读 digest/repo_status，编程交给 Cursor/Codex。"
    )
    return text[:200]


def build_snapshot(
    *,
    status: dict[str, Any],
    round_state: dict[str, Any],
    review_queue: dict[str, Any],
    manifest: dict[str, Any],
    reminder: str,
    digest_paths: dict[str, str],
) -> dict[str, Any]:
    repos = list(status.get("repos", []))
    open_items = [
        item
        for item in review_queue.get("items", [])
        if str(item.get("status", "")).lower() in OPEN_REVIEW_STATUSES
    ]
    top = daily_brief.pick_top_push(repos)
    return {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "role": "openclaw_daily_briefing_skill",
        "current_round": round_state.get("current_round"),
        "round_status": round_state.get("status"),
        "next_round": round_state.get("next_round"),
        "repo_count": len(repos),
        "blocked_repo_count": sum(1 for r in repos if r.get("blockers")),
        "status_generated_at": status.get("generated_at"),
        "top_repo_names": [r.get("name") for r in top],
        "review_queue_open_count": len(open_items),
        "digest_paths": digest_paths,
        "short_reminder": reminder,
        "dry_run_only": True,
        "external_api_called": False,
        "manifest_role": manifest.get("role"),
    }


def render_brief(
    template: str,
    *,
    status: dict[str, Any],
    review_queue: dict[str, Any],
    round_state: dict[str, Any],
    daily_briefing_path: Path,
    weekly_digest_path: Path,
    dry_run_commands: list[str],
) -> str:
    repos = list(status.get("repos", []))
    top = daily_brief.pick_top_push(repos)
    defer = daily_brief.pick_defer(repos)
    open_items = [
        item
        for item in review_queue.get("items", [])
        if str(item.get("status", "")).lower() in OPEN_REVIEW_STATUSES
    ]
    current_round = str(round_state.get("current_round", "—"))
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    replacements = {
        "{{generated_at}}": generated_at,
        "{{current_round}}": current_round,
        "{{round_status}}": str(round_state.get("status", "—")),
        "{{next_round}}": str(round_state.get("next_round", "—")),
        "{{repo_count}}": str(len(repos)),
        "{{blocked_repo_count}}": str(sum(1 for r in repos if r.get("blockers"))),
        "{{status_generated_at}}": str(status.get("generated_at", "—")),
        "{{top_repos}}": "\n".join(daily_brief.format_repo_line(r, i + 1) for i, r in enumerate(top))
        or "1. 暂无高优先级可推进仓",
        "{{defer_repos}}": "\n".join(daily_brief.format_repo_line(r) for r in defer) or "- 无",
        "{{daily_briefing_excerpt}}": excerpt_markdown(daily_briefing_path),
        "{{weekly_digest_excerpt}}": excerpt_markdown(weekly_digest_path),
        "{{review_queue_open}}": summarize_review_queue_open(review_queue),
        "{{dry_run_commands}}": "\n".join(dry_run_commands),
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
    parser = argparse.ArgumentParser(description="OpenClaw daily briefing skill (read-only, dry-run default)")
    parser.add_argument("--status", default="data/repo_status.example.json", help="Repo status JSON")
    parser.add_argument("--daily-briefing", default="governance/digests/daily/daily_briefing.md")
    parser.add_argument("--weekly-digest", default="governance/digests/weekly/weekly_digest.md")
    parser.add_argument("--review-queue", default="governance/review_queue.yaml")
    parser.add_argument("--round-state", default="round_state/current_round.yaml")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", default=DEFAULT_BRIEF)
    parser.add_argument("--snapshot", default=DEFAULT_SNAPSHOT)
    parser.add_argument("--dry-run", action="store_true", help="Print summary only; do not write files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status_path = Path(args.status)
    if not status_path.exists():
        raise SystemExit(f"Status not found: {status_path}")

    status = load_json(status_path)
    review_queue = load_yaml(Path(args.review_queue))
    round_state = load_yaml(Path(args.round_state))
    manifest = load_yaml(Path(args.manifest))
    template = load_text(Path(args.template))
    daily_briefing_path = Path(args.daily_briefing)
    weekly_digest_path = Path(args.weekly_digest)

    dry_run_commands = list(manifest.get("dry_run_triggers") or DEFAULT_DRY_RUN_COMMANDS)
    if "python3 scripts/openclaw_daily_briefing_skill.py --dry-run" not in dry_run_commands:
        dry_run_commands.insert(1, "python3 scripts/openclaw_daily_briefing_skill.py --dry-run")

    brief = render_brief(
        template,
        status=status,
        review_queue=review_queue,
        round_state=round_state,
        daily_briefing_path=daily_briefing_path,
        weekly_digest_path=weekly_digest_path,
        dry_run_commands=dry_run_commands,
    )

    repos = list(status.get("repos", []))
    open_items = [
        item
        for item in review_queue.get("items", [])
        if str(item.get("status", "")).lower() in OPEN_REVIEW_STATUSES
    ]
    reminder = build_short_reminder(
        top=daily_brief.pick_top_push(repos),
        defer=daily_brief.pick_defer(repos),
        review_open_count=len(open_items),
        current_round=str(round_state.get("current_round", "")),
    )
    snapshot = build_snapshot(
        status=status,
        round_state=round_state,
        review_queue=review_queue,
        manifest=manifest,
        reminder=reminder,
        digest_paths={
            "daily_briefing": str(daily_briefing_path),
            "weekly_digest": str(weekly_digest_path),
            "repo_status": str(status_path),
        },
    )

    print(
        f"[ok] openclaw daily briefing skill: repos={len(repos)} "
        f"review_open={len(open_items)} round={round_state.get('current_round', '—')}"
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
