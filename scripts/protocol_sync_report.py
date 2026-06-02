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

DEFAULT_POLICY = "config/protocol_sync_policy.yaml"

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


def governance_files_from_policy(policy: dict[str, Any]) -> list[str]:
    files = policy.get("governance_files")
    if isinstance(files, list) and files:
        return [str(f) for f in files]
    return GOVERNANCE_FILES


def skip_statuses_from_policy(policy: dict[str, Any]) -> set[str]:
    rules = policy.get("priority_rules", {})
    statuses = rules.get("skip_statuses", ["missing", "empty"])
    return {str(s).lower() for s in statuses}


def high_missing_from_policy(policy: dict[str, Any]) -> set[str]:
    rules = policy.get("priority_rules", {})
    items = rules.get("high_missing", ["AGENTS.md", "repo_protocol_standard.yaml"])
    return {str(x) for x in items}


def governance_status(repo: dict[str, Any], files: list[str]) -> tuple[list[str], list[str]]:
    read_files = set(repo.get("read_files", []))
    missing = set(str(x) for x in repo.get("missing", []))
    present: list[str] = []
    absent: list[str] = []
    for name in files:
        if name in read_files:
            present.append(name)
        elif name in missing or name not in read_files:
            absent.append(name)
    return present, absent


def suggest_priority(absent: list[str], high_missing: set[str]) -> str:
    if any(f in high_missing for f in absent):
        return "high"
    if absent:
        return "medium"
    return "none"


def render_repo_prompt(template: str, repo: dict[str, Any], protocol_version: str, files: list[str]) -> str:
    present, absent = governance_status(repo, files)
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


def build_yaml_payload(
    snapshots: dict[str, Any],
    protocol_version: str,
    *,
    files: list[str],
    skip_statuses: set[str],
    high_missing: set[str],
    status_source: str,
) -> dict[str, Any]:
    suggestions: list[dict[str, Any]] = []
    for repo in snapshots.get("repos", []):
        name = str(repo.get("name", ""))
        status = str(repo.get("status", "unknown")).lower()
        if status in skip_statuses:
            suggestions.append(
                {
                    "repo_name": name,
                    "status": status,
                    "action": "skip",
                    "priority": "none",
                    "missing_files": [],
                    "present_files": [],
                    "reason": f"status={status}",
                }
            )
            continue
        present, absent = governance_status(repo, files)
        priority = suggest_priority(absent, high_missing)
        suggestions.append(
            {
                "repo_name": name,
                "status": status,
                "action": "sync_suggested" if absent else "ok",
                "priority": priority,
                "missing_files": absent,
                "present_files": present,
                "reason": None if absent else "all governance files present",
            }
        )
    need_sync = [s for s in suggestions if s.get("action") == "sync_suggested"]
    return {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "reference_protocol_version": protocol_version,
        "status_source": status_source,
        "read_only": True,
        "summary": {
            "total_repos": len(suggestions),
            "need_sync": len(need_sync),
            "high_priority": sum(1 for s in need_sync if s.get("priority") == "high"),
            "skipped": sum(1 for s in suggestions if s.get("action") == "skip"),
        },
        "suggestions": suggestions,
    }


def dump_yaml_output(path: Path, data: dict[str, Any]) -> None:
    header = (
        "# Cross-repo protocol sync suggestions (read-only).\n"
        "# Generated by scripts/protocol_sync_report.py — do not auto-apply to managed repos.\n"
    )
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def build_report(
    snapshots: dict[str, Any],
    protocol_version: str,
    *,
    files: list[str],
    skip_statuses: set[str],
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
        if status.lower() in skip_statuses:
            lines.append(f"| {name} | {status} | （跳过：路径不可用） |")
            continue
        present, absent = governance_status(repo, files)
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
            "## 机器可读输出",
            "",
            "见 `governance/protocol_sync_suggestions.yaml`。",
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
    parser.add_argument("--policy", default=DEFAULT_POLICY, help="Protocol sync policy YAML")
    parser.add_argument("--input", default=None, help="Snapshots JSON (overrides policy)")
    parser.add_argument("--protocol", default=None, help="Reference protocol (overrides policy)")
    parser.add_argument("--output", default=None, help="Markdown report path (overrides policy)")
    parser.add_argument("--yaml-output", default=None, help="YAML output path (overrides policy)")
    parser.add_argument("--prompt-template", default=None, help="Prompt template (overrides policy)")
    parser.add_argument("--prompt-dir", default=None, help="Generated prompt directory (overrides policy)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only")
    parser.add_argument("--no-dry-run", action="store_false", dest="dry_run", help="Write prompt files")
    return parser.parse_args()


def resolve_paths(args: argparse.Namespace, policy: dict[str, Any]) -> dict[str, str]:
    sources = policy.get("sources", {})
    defaults = policy.get("defaults", {})
    write_prompts = not defaults.get("dry_run", True)
    if args.dry_run is False:
        write_prompts = True
    return {
        "input": args.input or str(sources.get("snapshots", "data/repo_snapshots.json")),
        "protocol": args.protocol or str(sources.get("reference_protocol", "repo_protocol_standard.yaml")),
        "output": args.output or str(sources.get("markdown_report", "reports/protocol_sync_suggestions.md")),
        "yaml_output": args.yaml_output or str(sources.get("yaml_output", "governance/protocol_sync_suggestions.yaml")),
        "prompt_template": args.prompt_template or str(sources.get("prompt_template", "prompts/protocol_sync_cursor.md")),
        "prompt_dir": args.prompt_dir or str(sources.get("prompt_dir", "prompts/generated")),
        "write_prompts": write_prompts,
    }


def main() -> int:
    args = parse_args()
    policy_path = Path(args.policy)
    policy = load_yaml(policy_path) if policy_path.exists() else {}
    paths = resolve_paths(args, policy)

    input_path = Path(paths["input"])
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    files = governance_files_from_policy(policy)
    skip_statuses = skip_statuses_from_policy(policy)
    high_missing = high_missing_from_policy(policy)

    snapshots = load_json(input_path)
    protocol = load_yaml(Path(paths["protocol"]))
    version = str(protocol.get("protocol_version", "unknown"))
    template_path = Path(paths["prompt_template"])
    template = load_text(template_path) if template_path.exists() else ""

    report_text, need_sync = build_report(snapshots, version, files=files, skip_statuses=skip_statuses)
    output_path = Path(paths["output"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_text, encoding="utf-8")

    yaml_payload = build_yaml_payload(
        snapshots,
        version,
        files=files,
        skip_statuses=skip_statuses,
        high_missing=high_missing,
        status_source=str(input_path.as_posix()),
    )
    yaml_path = Path(paths["yaml_output"])
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    dump_yaml_output(yaml_path, yaml_payload)

    written = 0
    if paths["write_prompts"] and template:
        prompt_dir = Path(paths["prompt_dir"])
        prompt_dir.mkdir(parents=True, exist_ok=True)
        repo_by_name = {str(r.get("name")): r for r in snapshots.get("repos", [])}
        for name, _status, _absent in need_sync:
            repo = repo_by_name.get(name)
            if not repo:
                continue
            prompt = render_repo_prompt(template, repo, version, files)
            out = prompt_dir / f"{name}_protocol_sync.md"
            out.write_text(prompt, encoding="utf-8")
            written += 1

    mode = "dry-run" if not paths["write_prompts"] else "write"
    print(
        f"[ok] protocol sync report ({mode}): {output_path} yaml={yaml_path} "
        f"need_sync={len(need_sync)} prompts={written}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
