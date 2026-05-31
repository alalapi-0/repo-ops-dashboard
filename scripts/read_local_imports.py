#!/usr/bin/env python3
"""Read optional local ICS/CSV paths and return markdown summary snippets."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def summarize_ics(path: Path) -> list[str]:
    if not path.is_file():
        return [f"日历文件不存在：{path}"]
    text = path.read_text(encoding="utf-8", errors="replace")
    summaries = re.findall(r"^SUMMARY:(.+)$", text, flags=re.MULTILINE)
    events = len(re.findall(r"^BEGIN:VEVENT", text, flags=re.MULTILINE))
    lines = [f"- 事件数：{events}"]
    for title in summaries[:5]:
        lines.append(f"- {title.strip()}")
    if len(summaries) > 5:
        lines.append(f"- … 另有 {len(summaries) - 5} 项")
    return lines


def summarize_csv(path: Path) -> list[str]:
    if not path.is_file():
        return [f"CSV 文件不存在：{path}"]
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return ["- （空文件）"]
    lines = [f"- 行数：{len(rows)}"]
    last = rows[-1]
    preview = ", ".join(f"{k}={v}" for k, v in list(last.items())[:4])
    lines.append(f"- 末行：{preview}")
    return lines


def build_imports_markdown(config: dict[str, Any]) -> str:
    lines = ["## 本地导入摘要", ""]
    ics_path = str(config.get("calendar_ics", "")).strip()
    csv_path = str(config.get("finance_csv", "")).strip()

    if not ics_path and not csv_path:
        lines.append("- 未配置 `config/local_imports.yaml`（可参考 example）")
        return "\n".join(lines) + "\n"

    if ics_path:
        lines.extend(["### 日历 (ICS)", ""] + summarize_ics(Path(ics_path)) + [""])
    if csv_path:
        lines.extend(["### 财务 (CSV)", ""] + summarize_csv(Path(csv_path)) + [""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize local ICS/CSV imports")
    parser.add_argument("--config", default="config/local_imports.yaml", help="Imports config yaml")
    parser.add_argument("--output", default="", help="Optional markdown output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.exists():
        config_path = Path("config/local_imports.example.yaml")
        config = load_yaml(config_path)
        # Use bundled samples when example has empty paths (demo mode)
        if not str(config.get("calendar_ics", "")).strip():
            config["calendar_ics"] = "data/sample_calendar.example.ics"
        if not str(config.get("finance_csv", "")).strip():
            config["finance_csv"] = "data/sample_finance.example.csv"
    else:
        config = load_yaml(config_path)

    markdown = build_imports_markdown(config)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown, encoding="utf-8")
        print(f"[ok] local imports summary -> {out}")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
