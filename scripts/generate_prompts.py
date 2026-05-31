#!/usr/bin/env python3
"""Generate per-repo Cursor/Codex/OpenClaw prompts from status data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_template(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def render(template: str, repo: dict[str, Any]) -> str:
    blockers = repo.get("blockers") or ["无"]
    next_actions = repo.get("next_actions") or ["无"]
    warnings = repo.get("warnings") or []
    replacements = {
        "{{repo_name}}": str(repo.get("name", "unknown")),
        "{{repo_type}}": str(repo.get("type", "unknown")),
        "{{priority}}": str(repo.get("priority", "unknown")),
        "{{health_score}}": str(repo.get("health_score", 0)),
        "{{current_stage}}": str(repo.get("current_stage", "unknown")),
        "{{blockers}}": "; ".join(blockers),
        "{{next_actions}}": "; ".join(next_actions),
        "{{warnings}}": "; ".join(warnings) if warnings else "无",
        "{{generated_at}}": datetime.now(timezone.utc).isoformat(),
    }
    text = template
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def build_fallback(agent: str, repo: dict[str, Any]) -> str:
    name = repo.get("name", "unknown")
    blockers = "; ".join(repo.get("blockers") or ["无"])
    next_actions = "; ".join(repo.get("next_actions") or ["无"])
    return (
        f"# {agent} Prompt — {name}\n\n"
        f"仓库：{name}\n"
        f"类型：{repo.get('type')}\n"
        f"优先级：{repo.get('priority')}\n"
        f"健康分：{repo.get('health_score')}\n\n"
        f"## 卡点\n{blockers}\n\n"
        f"## 下一步\n{next_actions}\n\n"
        "## 边界\n"
        "- 不读取 .env 与密钥\n"
        "- 不修改被管理业务仓库\n"
        "- 默认 dry-run\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate agent prompts from repo status")
    parser.add_argument("--input", default="data/repo_status.json", help="Input status json")
    parser.add_argument("--output-dir", default="prompts/generated", help="Output directory")
    parser.add_argument("--prompts-dir", default="prompts", help="Template directory")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only")
    parser.add_argument("--no-dry-run", action="store_false", dest="dry_run", help="Write prompt files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    prompts_dir = Path(args.prompts_dir)

    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    payload = load_json(input_path)
    repos = list(payload.get("repos", []))

    templates = {
        "cursor": load_template(prompts_dir / "cursor_next_round.md"),
        "codex": load_template(prompts_dir / "codex_next_round.md"),
        "openclaw": load_template(prompts_dir / "openclaw_repo_scan.md"),
    }

    print(f"[prompts] repos={len(repos)} dry_run={args.dry_run}")
    for repo in repos:
        name = str(repo.get("name", "unknown"))
        safe_name = name.replace("/", "_")
        for agent, template in templates.items():
            content = render(template, repo) if template else build_fallback(agent, repo)
            out_path = output_dir / f"{safe_name}_{agent}.md"
            print(f"[prompt] {out_path.name} ({len(content)} chars)")
            if not args.dry_run:
                output_dir.mkdir(parents=True, exist_ok=True)
                out_path.write_text(content, encoding="utf-8")

    if args.dry_run:
        print("[dry-run] prompt files not written")
        return 0

    print(f"[ok] wrote prompts to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
