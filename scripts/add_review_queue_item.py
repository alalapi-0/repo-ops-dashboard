#!/usr/bin/env python3
"""Append an open review_queue item (Agent may create, not close)."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

from validate_review_queue import (  # noqa: E402
    build_review_item,
    read_review_queue,
    validate_item,
    validate_review_queue,
)


def dump_queue(path: Path, data: dict) -> None:
    header = (
        "# Review queue (Human-in-the-loop).\n"
        "# Agents may append open items; only HumanOwner closes via close_review_queue_item.py\n"
    )
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append an open review_queue item")
    parser.add_argument("--queue", default="governance/review_queue.yaml")
    parser.add_argument("--review-id", required=True)
    parser.add_argument("--type", required=True, dest="type_")
    parser.add_argument("--project-id", default="repo_ops_dashboard")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--options", required=True, help="Comma-separated allowed options")
    parser.add_argument("--context-ref", action="append", dest="context_refs", default=[])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.queue)
    try:
        queue = read_review_queue(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}", file=sys.stderr)
        return 1

    options = [part.strip() for part in args.options.split(",") if part.strip()]
    item = build_review_item(
        review_id=args.review_id,
        type_=args.type_,
        project_id=args.project_id,
        task_id=args.task_id,
        prompt=args.prompt,
        options=options,
        context_refs=args.context_refs,
    )
    errors = validate_item(item, args.review_id)
    if errors:
        for err in errors:
            print(f"[error] {err}", file=sys.stderr)
        return 2

    existing_ids = {str(row.get("review_id")) for row in queue.get("items") or []}
    if args.review_id in existing_ids:
        print(f"[error] duplicate review_id: {args.review_id}", file=sys.stderr)
        return 2

    queue.setdefault("items", []).append(item)
    queue["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    queue_errors = validate_review_queue(queue, path.name)
    if queue_errors:
        for err in queue_errors:
            print(f"[error] {err}", file=sys.stderr)
        return 2

    print(f"[ok] review item ready: {args.review_id} (status=open)")
    if args.dry_run:
        print("[dry-run] file not written")
        return 0

    dump_queue(path, queue)
    print(f"[ok] appended to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
