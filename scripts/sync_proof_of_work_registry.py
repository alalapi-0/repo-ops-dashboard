#!/usr/bin/env python3
"""Build governance/proof_of_work_registry.yaml from proof_of_work/*.json."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

from validate_proof_of_work import (  # noqa: E402
    discover_proof_files,
    read_proof_of_work,
    validate_proof_of_work,
)

def dump_registry(path: Path, data: dict[str, Any]) -> None:
    header = (
        "# Proof of work registry (Personal Agent OS).\n"
        "# Sources: governance/proof_of_work/*.json via scripts/sync_proof_of_work_registry.py\n"
    )
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def record_to_entry(record: dict[str, Any], record_path: Path, root: Path) -> dict[str, Any]:
    rel = record_path.relative_to(root).as_posix() if record_path.is_relative_to(root) else str(record_path)
    return {
        "task_id": record.get("task_id"),
        "project_id": record.get("project_id"),
        "status": record.get("status"),
        "completed_at": record.get("completed_at"),
        "agent_type": record.get("agent_type"),
        "tests_passed": record.get("tests_passed"),
        "proof_path": rel,
        "summary": record.get("summary"),
        "known_issue_count": len(record.get("known_issues") or []),
    }


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    for row in records:
        status = str(row.get("status", "unknown"))
        by_status[status] = by_status.get(status, 0) + 1
    passed = sum(1 for row in records if row.get("tests_passed") is True)
    return {
        "total_records": len(records),
        "tests_passed_count": passed,
        "by_status": by_status,
    }


def build_registry(root: Path, pow_dir: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    entries: list[dict[str, Any]] = []
    for record_path in discover_proof_files(pow_dir):
        try:
            record = read_proof_of_work(record_path)
        except (json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{record_path.name}: load failed: {exc}")
            continue
        record_errors = validate_proof_of_work(record, record_path.name)
        errors.extend(record_errors)
        if not record_errors:
            entries.append(record_to_entry(record, record_path, root))
    entries.sort(key=lambda row: str(row.get("task_id", "")))
    payload = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "proof_of_work_dir": pow_dir.relative_to(root).as_posix() if pow_dir.is_relative_to(root) else str(pow_dir),
        "summary": build_summary(entries),
        "records": entries,
    }
    return payload, errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync governance/proof_of_work_registry.yaml")
    parser.add_argument("--pow-dir", default="governance/proof_of_work")
    parser.add_argument("--output", default="governance/proof_of_work_registry.yaml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print registry JSON (implies dry-run)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    pow_dir = Path(args.pow_dir)
    output_path = Path(args.output)

    if not pow_dir.is_dir():
        raise SystemExit(f"proof_of_work directory not found: {pow_dir}")

    payload, errors = build_registry(root, pow_dir)
    if errors:
        for err in errors:
            print(f"[error] {err}")
        return 2

    summary = payload["summary"]
    print(
        f"[ok] proof_of_work registry: {summary['total_records']} record(s), "
        f"tests_passed={summary['tests_passed_count']}"
    )

    if args.json or args.dry_run:
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("[dry-run] file not written")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dump_registry(output_path, payload)
    print(f"[ok] wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
