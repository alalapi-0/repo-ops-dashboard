#!/usr/bin/env python3
"""Read and validate governance/review_queue.yaml."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

from validate_review_queue import (  # noqa: E402
    OPEN_STATUSES,
    read_review_queue,
    summarize_review_queue,
    validate_review_queue,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read and validate review_queue.yaml")
    parser.add_argument("path", nargs="?", default="governance/review_queue.yaml")
    parser.add_argument("--status", choices=["open", "decided", "all"], default="all")
    parser.add_argument("--json", action="store_true", help="Output filtered items as JSON")
    return parser.parse_args()


def filter_items(items: list[dict], status: str) -> list[dict]:
    if status == "all":
        return items
    if status == "open":
        return [item for item in items if str(item.get("status", "")).lower() in OPEN_STATUSES]
    return [item for item in items if str(item.get("status", "")).lower() == "decided"]


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    try:
        queue = read_review_queue(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    errors = validate_review_queue(queue, path.name)
    if errors:
        for err in errors:
            print(f"[error] {err}", file=sys.stderr)
        return 2

    summary = summarize_review_queue(queue)
    items = filter_items(list(queue.get("items") or []), args.status)
    print(
        f"[ok] review_queue valid: {summary['total_items']} item(s), "
        f"open={summary['open_items']}, decided={summary['decided_items']}"
    )
    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
    else:
        print(yaml.safe_dump(items, allow_unicode=True, sort_keys=False, default_flow_style=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
