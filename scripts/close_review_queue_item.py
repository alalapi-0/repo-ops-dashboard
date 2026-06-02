#!/usr/bin/env python3
"""Close a review_queue item — HumanOwner only."""

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

from validate_review_queue import OPEN_STATUSES, read_review_queue, validate_review_queue  # noqa: E402


ALLOWED_ACTORS = frozenset({"human_owner"})


def dump_queue(path: Path, data: dict) -> None:
    header = (
        "# Review queue (Human-in-the-loop).\n"
        "# Agents may append open items; only HumanOwner closes via close_review_queue_item.py\n"
    )
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Close a review_queue item (HumanOwner only)")
    parser.add_argument("--queue", default="governance/review_queue.yaml")
    parser.add_argument("--review-id", required=True)
    parser.add_argument("--decision", required=True, help="Final decision value from item options")
    parser.add_argument("--actor", required=True, help="Must be human_owner")
    parser.add_argument("--status", default="decided", choices=["decided", "cancelled", "expired"])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    actor = args.actor.strip().lower()
    if actor not in ALLOWED_ACTORS:
        print(f"[error] only HumanOwner may close items (--actor {args.actor})", file=sys.stderr)
        return 2

    path = Path(args.queue)
    try:
        queue = read_review_queue(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}", file=sys.stderr)
        return 1

    items = list(queue.get("items") or [])
    target = None
    for item in items:
        if str(item.get("review_id")) == args.review_id:
            target = item
            break
    if target is None:
        print(f"[error] review_id not found: {args.review_id}", file=sys.stderr)
        return 2

    status = str(target.get("status", "")).lower()
    if status not in OPEN_STATUSES:
        print(f"[error] item not open: status={status}", file=sys.stderr)
        return 2

    options = [str(opt) for opt in target.get("options") or []]
    if args.status == "decided" and options and args.decision not in options:
        print(f"[error] decision must be one of: {options}", file=sys.stderr)
        return 2

    target["status"] = args.status
    target["decision"] = args.decision if args.status == "decided" else args.decision
    target["decided_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    queue["updated_at"] = target["decided_at"]

    errors = validate_review_queue(queue, path.name)
    if errors:
        for err in errors:
            print(f"[error] {err}", file=sys.stderr)
        return 2

    print(f"[ok] review item closed: {args.review_id} -> {args.status} ({args.decision})")
    if args.dry_run:
        print("[dry-run] file not written")
        return 0

    dump_queue(path, queue)
    print(f"[ok] updated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
