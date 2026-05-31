#!/usr/bin/env python3
"""Generate markdown daily and weekly reports from repository status data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def section_from_repos(title: str, repos: list[dict[str, Any]]) -> str:
    lines = [f"## {title}"]
    if not repos:
        lines.append("- 无")
        return "\n".join(lines)
    for repo in repos:
        lines.append(
            f"- **{repo.get('name')}** | priority={repo.get('priority')} | "
            f"score={repo.get('health_score')} | agent={repo.get('recommended_agent')}"
        )
        blockers = repo.get("blockers", [])
        if blockers:
            lines.append(f"  - blockers: {'; '.join(blockers)}")
        next_actions = repo.get("next_actions", [])
        if next_actions:
            lines.append(f"  - next: {'; '.join(next_actions)}")
    return "\n".join(lines)


def build_report(title: str, payload: dict[str, Any]) -> str:
    repos = list(payload.get("repos", []))
    high = [repo for repo in repos if repo.get("priority") == "high"]
    blocked = [repo for repo in repos if repo.get("blockers")]
    freeze = [repo for repo in repos if repo.get("freeze_candidate")]
    archive = [repo for repo in repos if repo.get("archive_candidate")]
    cursor_tasks = [repo for repo in repos if repo.get("recommended_agent") == "Cursor"]
    codex_tasks = [repo for repo in repos if repo.get("recommended_agent") == "Codex"]

    content = [
        f"# {title}",
        "",
        f"- 生成时间: {datetime.now(timezone.utc).isoformat()}",
        f"- 仓库总数: {len(repos)}",
        "",
        section_from_repos("高优先级仓库", high),
        "",
        section_from_repos("卡住的仓库", blocked),
        "",
        section_from_repos("建议冻结的仓库", freeze),
        "",
        section_from_repos("建议归档的仓库", archive),
        "",
        section_from_repos("本周建议推进事项", high[:5]),
        "",
        section_from_repos("推荐交给 Cursor 的任务", cursor_tasks),
        "",
        section_from_repos("推荐交给 Codex 的任务", codex_tasks),
        "",
    ]
    return "\n".join(content)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate markdown reports from repo status")
    parser.add_argument("--input", default="data/repo_status.json", help="Input status json")
    parser.add_argument(
        "--output",
        default="reports/daily_repo_report.md",
        help="Daily report output markdown path",
    )
    parser.add_argument(
        "--weekly-output",
        default="reports/weekly_repo_report.md",
        help="Weekly report output markdown path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    daily_output = Path(args.output)
    weekly_output = Path(args.weekly_output)

    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    payload = load_json(input_path)

    daily_output.parent.mkdir(parents=True, exist_ok=True)
    weekly_output.parent.mkdir(parents=True, exist_ok=True)

    daily_output.write_text(build_report("Repo Ops Daily Report", payload), encoding="utf-8")
    weekly_output.write_text(build_report("Repo Ops Weekly Report", payload), encoding="utf-8")

    print(f"[ok] daily report: {daily_output}")
    print(f"[ok] weekly report: {weekly_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
