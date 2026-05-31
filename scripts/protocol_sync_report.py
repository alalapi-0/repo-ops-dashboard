#!/usr/bin/env python3
"""Generate cross-repo protocol sync suggestions (read-only, no managed repo writes)."""

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


GOVERNANCE_FILES = [
    "README.md",
    "AGENTS.md",
    "repo_protocol_standard.yaml",
    "CHANGELOG.md",
    "docs/index.md",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def governance_status(repo: dict[str, Any]) -> tuple[list[str], list[str]]:
    read_files = set(repo.get("read_files", []))
    missing = set(str(x) for x in repo.get("missing", []))
    present: list[str] = []
    absent: list[str] = []
    for name in GOVERNANCE_FILES:
        if name in read_files:
            present.append(name)
        elif name in missing or name not in read_files:
            absent.append(name)
    return present, absent


def render_repo_prompt(template: str, repo: dict[str, Any], protocol_version: str) -> str:
    present, absent = governance_status(repo)
    text = template
    replacements = {
        "{{repo_name}}": str(repo.get("name", "unknown")),
        "{{missing_governance}}": ", ".join(absent) or "无",
        "{{present_governance}}": ", ".join(present) or "无",
        "{{protocol_version}}": protocol_version,
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def build_report(
    snapshots: dict[str, Any],
    protocol_version: str,
) -> tuple[str, list[tuple[str, str, list[str]]]]:
    rows: list[tuple[str, str, list[str]]] = []
    lines = [
        "# Protocol Sync Suggestions",
        "",
        f"- generated_at: {datetime.now(timezone.utc).isoformat()}",
        f"- reference_protocol_version: {protocol_version}",
        "- **只读建议**：不在此脚本中写入任何被管理仓库。",
        "",
        "## 各仓差异",
        "",
        "| 仓库 | 状态 | 缺失治理文件 |",
        "|------|------|--------------|",
    ]

    for repo in snapshots.get("repos", []):
        name = str(repo.get("name", ""))
        status = str(repo.get("status", "unknown"))
        if status in {"missing", "empty"}:
            lines.append(f"| {name} | {status} | （跳过：路径不可用） |")
            continue
        present, absent = governance_status(repo)
        if absent:
            rows.append((name, status, absent))
            lines.append(f"| {name} | {status} | {', '.join(absent)} |")
        else:
            lines.append(f"| {name} | {status} | — |")

    lines.extend(
        [
            "",
            "## 建议执行顺序",
            "",
            "1. 高优先级且缺失 `AGENTS.md` / `repo_protocol_standard.yaml` 的 active 仓库",
            "2. 仅有 README/CHANGELOG 缺失的中优先级仓库",
            "3. archived / missing 路径 — Human 决策是否保留登记",
            "",
            "## 生成的 Cursor Prompt",
            "",
            "见 `prompts/generated/<repo>_protocol_sync.md`（需 `--no-dry-run` 写入）。",
            "",
        ]
    )
    return "\n".join(lines), rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Protocol sync suggestion report")
    parser.add_argument("--input", default="data/repo_snapshots.json", help="Snapshots JSON")
    parser.add_argument("--protocol", default="repo_protocol_standard.yaml", help="Reference protocol")
    parser.add_argument("--output", default="reports/protocol_sync_suggestions.md", help="Report path")
    parser.add_argument("--prompt-template", default="prompts/protocol_sync_cursor.md", help="Prompt template")
    parser.add_argument("--prompt-dir", default="prompts/generated", help="Generated prompt directory")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only")
    parser.add_argument("--no-dry-run", action="store_false", dest="dry_run", help="Write prompt files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    snapshots = load_json(input_path)
    protocol = load_yaml(Path(args.protocol))
    version = str(protocol.get("protocol_version", "unknown"))
    template = load_text(Path(args.prompt_template))

    report_text, need_sync = build_report(snapshots, version)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_text, encoding="utf-8")

    written = 0
    if not args.dry_run and template:
        prompt_dir = Path(args.prompt_dir)
        prompt_dir.mkdir(parents=True, exist_ok=True)
        repo_by_name = {str(r.get("name")): r for r in snapshots.get("repos", [])}
        for name, _status, _absent in need_sync:
            repo = repo_by_name.get(name)
            if not repo:
                continue
            prompt = render_repo_prompt(template, repo, version)
            out = prompt_dir / f"{name}_protocol_sync.md"
            out.write_text(prompt, encoding="utf-8")
            written += 1

    mode = "dry-run" if args.dry_run else "write"
    print(f"[ok] protocol sync report ({mode}): {output_path} need_sync={len(need_sync)} prompts={written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
