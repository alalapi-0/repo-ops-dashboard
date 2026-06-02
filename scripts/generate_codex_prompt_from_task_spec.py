#!/usr/bin/env python3
"""Generate a Codex prompt from a governance task_spec YAML file."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_FIELDS = (
    "task_id",
    "project_id",
    "title",
    "working_directory",
    "assigned_agent",
    "acceptance_criteria",
)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"task_spec must be a mapping: {path}")
    return data


def load_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def format_list(items: Any, *, empty_label: str = "无") -> str:
    if not items:
        return empty_label
    if isinstance(items, list):
        return "\n".join(f"- {item}" for item in items)
    return str(items)


def validate_task_spec(spec: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""
    for field in REQUIRED_FIELDS:
        if not str(spec.get(field, "")).strip():
            errors.append(f"{prefix}missing required field: {field}")
    agent = str(spec.get("assigned_agent", "")).strip()
    if agent and agent != "Codex":
        errors.append(f"{prefix}assigned_agent must be Codex for this generator (got {agent!r})")
    return errors


def render_task_spec(template: str, spec: dict[str, Any]) -> str:
    replacements = {
        "{{task_id}}": str(spec.get("task_id", "")),
        "{{project_id}}": str(spec.get("project_id", "")),
        "{{title}}": str(spec.get("title", "")),
        "{{description}}": str(spec.get("description", "")),
        "{{status}}": str(spec.get("status", "")),
        "{{priority}}": str(spec.get("priority", "")),
        "{{task_type}}": str(spec.get("task_type", "")),
        "{{working_directory}}": str(spec.get("working_directory", "")),
        "{{scope}}": format_list(spec.get("scope")),
        "{{out_of_scope}}": format_list(spec.get("out_of_scope")),
        "{{reference_paths}}": format_list(spec.get("reference_paths")),
        "{{acceptance_criteria}}": format_list(spec.get("acceptance_criteria")),
        "{{artifacts_expected}}": format_list(spec.get("artifacts_expected")),
        "{{validation_commands}}": format_list(spec.get("validation_commands")),
        "{{blockers}}": format_list(spec.get("blockers")),
        "{{playbook_id}}": str(spec.get("playbook_id", "")),
        "{{confirmation_policy}}": str(spec.get("confirmation_policy", "")),
        "{{execpolicy_profile}}": str(spec.get("execpolicy_profile", "")),
        "{{generated_at}}": datetime.now(timezone.utc).isoformat(),
    }
    text = template
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def build_fallback(spec: dict[str, Any]) -> str:
    task_id = spec.get("task_id", "unknown")
    return (
        f"# Codex Prompt — {task_id}\n\n"
        f"项目：{spec.get('project_id')}\n"
        f"工作目录：{spec.get('working_directory')}\n\n"
        f"## 描述\n{spec.get('description', '')}\n\n"
        "## 边界\n"
        "- 不读取 .env 与密钥\n"
        "- 不修改被管理业务仓库\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Codex prompt from task_spec YAML")
    parser.add_argument(
        "--task-spec",
        default="governance/task_specs/example_codex_task_spec.yaml",
        help="Input task_spec YAML path",
    )
    parser.add_argument(
        "--template",
        default="prompts/codex_from_task_spec.md",
        help="Prompt template path",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Output markdown path (default: prompts/generated/<task_id>_codex.md)",
    )
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only")
    parser.add_argument("--no-dry-run", action="store_false", dest="dry_run", help="Write prompt file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec_path = Path(args.task_spec)
    template_path = Path(args.template)

    if not spec_path.exists():
        raise SystemExit(f"task_spec not found: {spec_path}")

    spec = load_yaml(spec_path)
    errors = validate_task_spec(spec, spec_path.name)
    if errors:
        for err in errors:
            print(f"[error] {err}", file=sys.stderr)
        return 1

    template = load_template(template_path) if template_path.exists() else ""
    content = render_task_spec(template, spec) if template else build_fallback(spec)

    task_id = str(spec.get("task_id", "task"))
    safe_id = task_id.replace("/", "_")
    out_path = Path(args.output) if args.output else Path("prompts/generated") / f"{safe_id}_codex.md"

    print(f"[codex_prompt] task={task_id} chars={len(content)} dry_run={args.dry_run}")
    print(f"[codex_prompt] output={out_path}")
    if not args.dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"[ok] wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
