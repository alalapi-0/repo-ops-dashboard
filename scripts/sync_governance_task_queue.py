#!/usr/bin/env python3
"""Build governance/governance_task_queue.yaml from task_specs/*.yaml."""

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

TEMPLATE_NAME = "task_spec.template.yaml"
REQUIRED_TASK_SPEC_FIELDS = (
    "task_id",
    "project_id",
    "title",
    "status",
    "priority",
    "working_directory",
    "assigned_agent",
    "acceptance_criteria",
    "validation_commands",
    "execpolicy_profile",
)

ACTIVE_STATUSES = {"proposed", "ready", "in_progress", "blocked"}
TERMINAL_STATUSES = {"completed", "cancelled", "archived"}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def dump_queue(path: Path, data: dict[str, Any]) -> None:
    header = (
        "# Governance task queue (Personal Agent OS).\n"
        "# Sources: governance/task_specs/*.yaml via scripts/sync_governance_task_queue.py\n"
    )
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def discover_task_specs(specs_dir: Path) -> list[Path]:
    if not specs_dir.is_dir():
        return []
    paths = sorted(specs_dir.glob("*.yaml"))
    return [p for p in paths if p.name != TEMPLATE_NAME]


def validate_task_spec(data: dict[str, Any], source: str = "") -> list[str]:
    errors: list[str] = []
    prefix = f"{source}: " if source else ""
    missing = [field for field in REQUIRED_TASK_SPEC_FIELDS if not data.get(field)]
    if missing:
        errors.append(f"{prefix}missing fields: {missing}")
    task_id = str(data.get("task_id", "")).strip()
    if task_id and not task_id.startswith("task_"):
        errors.append(f"{prefix}task_id should start with task_")
    wd = str(data.get("working_directory", ""))
    if wd and (".env" in wd.lower() or "secret" in wd.lower()):
        errors.append(f"{prefix}working_directory looks unsafe")
    return errors


def read_task_spec(path: Path) -> dict[str, Any]:
    """Load and return a single task_spec YAML document."""
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def task_to_queue_entry(spec: dict[str, Any], spec_path: Path, root: Path) -> dict[str, Any]:
    rel = spec_path.relative_to(root).as_posix() if spec_path.is_relative_to(root) else str(spec_path)
    status = str(spec.get("status", "proposed"))
    entry: dict[str, Any] = {
        "task_id": spec.get("task_id"),
        "project_id": spec.get("project_id"),
        "title": spec.get("title"),
        "status": status,
        "priority": spec.get("priority"),
        "task_type": spec.get("task_type"),
        "assigned_agent": spec.get("assigned_agent"),
        "execpolicy_profile": spec.get("execpolicy_profile"),
        "confirmation_policy": spec.get("confirmation_policy"),
        "task_spec_path": rel,
        "is_active": status in ACTIVE_STATUSES,
    }
    if spec.get("blockers"):
        entry["blockers"] = list(spec.get("blockers") or [])
    if spec.get("depends_on"):
        entry["depends_on"] = list(spec.get("depends_on") or [])
    return entry


def build_summary(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    for task in tasks:
        status = str(task.get("status", "unknown"))
        by_status[status] = by_status.get(status, 0) + 1
    active = sum(1 for t in tasks if t.get("is_active"))
    return {
        "total_tasks": len(tasks),
        "active_tasks": active,
        "by_status": by_status,
    }


def build_queue(root: Path, specs_dir: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    entries: list[dict[str, Any]] = []
    for spec_path in discover_task_specs(specs_dir):
        try:
            spec = read_task_spec(spec_path)
        except Exception as exc:  # pragma: no cover - rare IO
            errors.append(f"{spec_path.name}: load failed: {exc}")
            continue
        spec_errors = validate_task_spec(spec, spec_path.name)
        errors.extend(spec_errors)
        if not spec_errors:
            entries.append(task_to_queue_entry(spec, spec_path, root))
    entries.sort(key=lambda row: (str(row.get("priority", "")), str(row.get("task_id", ""))))
    payload = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "task_specs_dir": specs_dir.relative_to(root).as_posix() if specs_dir.is_relative_to(root) else str(specs_dir),
        "summary": build_summary(entries),
        "tasks": entries,
    }
    return payload, errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync governance/governance_task_queue.yaml from task_specs")
    parser.add_argument("--specs-dir", default="governance/task_specs")
    parser.add_argument("--output", default="governance/governance_task_queue.yaml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print queue JSON to stdout (implies dry-run)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    specs_dir = Path(args.specs_dir)
    output_path = Path(args.output)

    if not specs_dir.is_dir():
        raise SystemExit(f"Task specs directory not found: {specs_dir}")

    payload, errors = build_queue(root, specs_dir)
    if errors:
        for err in errors:
            print(f"[error] {err}")
        return 2

    summary = payload["summary"]
    print(
        f"[ok] task queue: {summary['total_tasks']} task(s), "
        f"active={summary['active_tasks']}"
    )

    if args.json or args.dry_run:
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("[dry-run] file not written")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dump_queue(output_path, payload)
    print(f"[ok] wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
