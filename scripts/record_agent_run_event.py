#!/usr/bin/env python3
"""Append a validated agent_run event to governance/runs/{run_id}.jsonl."""

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

from validate_agent_run import build_event, validate_event  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append one agent_run JSONL event (manual audit trail)")
    parser.add_argument("--run-id", required=True, help="Run identifier used for governance/runs/{run_id}.jsonl")
    parser.add_argument("--event-type", required=True, help="Audit event type")
    parser.add_argument("--task-id", required=True, help="Governance task_id")
    parser.add_argument("--project-id", default="repo_ops_dashboard")
    parser.add_argument("--agent-type", default="Cursor")
    parser.add_argument("--cwd", default=".", help="Working directory for the event")
    parser.add_argument("--timestamp", help="ISO 8601 timestamp (defaults to now UTC)")
    parser.add_argument("--payload-json", default="{}", help="JSON object payload")
    parser.add_argument("--error", help="Optional error string")
    parser.add_argument("--proof-of-work-path", help="Optional proof_of_work path")
    parser.add_argument("--runs-dir", default="governance/runs")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print without writing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = json.loads(args.payload_json)
    except json.JSONDecodeError as exc:
        print(f"[error] invalid --payload-json: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("[error] --payload-json must be a JSON object", file=sys.stderr)
        return 2

    timestamp = args.timestamp or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    event = build_event(
        event_type=args.event_type,
        timestamp=timestamp,
        task_id=args.task_id,
        project_id=args.project_id,
        agent_type=args.agent_type,
        cwd=str(Path(args.cwd).resolve()),
        payload=payload,
        error=args.error,
        proof_of_work_path=args.proof_of_work_path,
    )
    errors = validate_event(event, args.run_id)
    if errors:
        for err in errors:
            print(f"[error] {err}", file=sys.stderr)
        return 2

    line = json.dumps(event, ensure_ascii=False)
    output_path = Path(args.runs_dir) / f"{args.run_id}.jsonl"
    print(f"[ok] event valid: {event.get('event_type')} -> {output_path}")

    if args.dry_run:
        print("[dry-run] file not written")
        print(line)
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(f"[ok] appended to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
