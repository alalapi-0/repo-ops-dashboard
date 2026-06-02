#!/usr/bin/env python3
"""Read and validate an agent_run JSONL audit trail file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from validate_agent_run import read_agent_run, validate_agent_run  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read and validate an agent_run JSONL file")
    parser.add_argument("path", help="Path to *.jsonl audit trail")
    parser.add_argument("--json", action="store_true", help="Output events as JSON array")
    parser.add_argument(
        "--event-type",
        action="append",
        dest="event_types",
        help="Filter by event_type (repeatable)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    try:
        events = read_agent_run(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    errors = validate_agent_run(path)
    if errors:
        for err in errors:
            print(f"[error] {err}", file=sys.stderr)
        return 2

    if args.event_types:
        allowed = {item.strip() for item in args.event_types if item.strip()}
        events = [event for event in events if event.get("event_type") in allowed]

    print(f"[ok] agent_run valid: {path.name} ({len(events)} event(s))")
    if args.json:
        print(json.dumps(events, ensure_ascii=False, indent=2))
    else:
        for event in events:
            print(json.dumps(event, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
