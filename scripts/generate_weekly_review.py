#!/usr/bin/env python3
"""Merge priority review, OpenClaw brief, weekly report, and human notes into one review."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_text(path: Path) -> str:
    if not path.exists():
        return f"（未找到：{path}）\n"
    return path.read_text(encoding="utf-8").strip() + "\n"


def load_human_notes(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def format_human_section(notes: dict[str, Any]) -> str:
    if not notes:
        return "- 无（可编辑 `data/human_notes.json`，参考 example）\n"
    lines = [
        f"- 周次：{notes.get('week_label', '—')}",
        f"- 更新：{notes.get('updated_at', '—')}",
        "",
    ]
    for item in notes.get("notes", []):
        lines.append(f"- {item}")
    focus = notes.get("focus_repos", [])
    if focus:
        lines.extend(["", f"- 关注仓库：{', '.join(str(x) for x in focus)}"])
    return "\n".join(lines) + "\n"


def build_review(
    *,
    priority_text: str,
    brief_text: str,
    weekly_text: str,
    human_notes: dict[str, Any],
    imports_text: str = "",
) -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    sections = [
        "# Repo Ops Weekly Review",
        "",
        f"- generated_at: {generated_at}",
        "- 来源：priority_review + openclaw_daily_brief + weekly_repo_report + human_notes",
        "",
        "## Human 本周笔记",
        "",
        format_human_section(human_notes),
    ]
    if imports_text.strip():
        sections.extend([imports_text.strip(), ""])
    sections.extend(
        [
            "## 优先级复盘摘要",
            "",
            priority_text,
            "## OpenClaw 每日简报",
            "",
            brief_text,
            "## 周报原始数据",
            "",
            weekly_text,
        ]
    )
    return "\n".join(sections)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate merged weekly review markdown")
    parser.add_argument(
        "--priority-report",
        default="reports/priority_review.md",
        help="Priority review markdown",
    )
    parser.add_argument(
        "--brief",
        default="reports/openclaw_daily_brief.md",
        help="OpenClaw daily brief markdown",
    )
    parser.add_argument(
        "--weekly",
        default="reports/weekly_repo_report.md",
        help="Weekly repo report markdown",
    )
    parser.add_argument(
        "--human-notes",
        default="data/human_notes.json",
        help="Human notes JSON (optional)",
    )
    parser.add_argument(
        "--imports-config",
        default="config/local_imports.yaml",
        help="Local ICS/CSV paths yaml",
    )
    parser.add_argument(
        "--output",
        default="reports/weekly_review.md",
        help="Merged weekly review output",
    )
    return parser.parse_args()


def load_imports_summary(config_path: Path) -> str:
    try:
        from read_local_imports import build_imports_markdown, load_yaml as load_imports_yaml
    except ImportError:
        return ""
    if config_path.exists():
        config = load_imports_yaml(config_path)
    else:
        example = Path("config/local_imports.example.yaml")
        config = load_imports_yaml(example) if example.exists() else {}
        if not str(config.get("calendar_ics", "")).strip():
            config["calendar_ics"] = "data/sample_calendar.example.ics"
        if not str(config.get("finance_csv", "")).strip():
            config["finance_csv"] = "data/sample_finance.example.csv"
    return build_imports_markdown(config)


def main() -> int:
    args = parse_args()
    human_path = Path(args.human_notes)
    if not human_path.exists():
        example = Path("data/human_notes.example.json")
        human_notes = load_human_notes(example) if example.exists() else {}
    else:
        human_notes = load_human_notes(human_path)

    review = build_review(
        priority_text=load_text(Path(args.priority_report)),
        brief_text=load_text(Path(args.brief)),
        weekly_text=load_text(Path(args.weekly)),
        human_notes=human_notes,
        imports_text=load_imports_summary(Path(args.imports_config)),
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(review, encoding="utf-8")
    print(f"[ok] weekly review -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
