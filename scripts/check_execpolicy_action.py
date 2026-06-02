#!/usr/bin/env python3
"""Check a proposed path or command against execpolicy rules (dry-run advisory)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from validate_execpolicy import (  # noqa: E402
    KNOWN_PROFILES,
    classify_command,
    classify_path,
    load_profile_rules,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check execpolicy for a path or command")
    parser.add_argument("--profile", default="repo_ops_write", choices=list(KNOWN_PROFILES))
    parser.add_argument("--action", choices=["read", "write"], help="Path access type")
    parser.add_argument("--path", help="Target path to classify")
    parser.add_argument("--command", help="Shell command to classify")
    parser.add_argument("--dry-run", action="store_true", help="Advisory only (default behaviour)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.path and not args.command:
        print("[error] specify --path or --command", file=sys.stderr)
        return 2
    if args.path and not args.action:
        print("[error] --path requires --action read|write", file=sys.stderr)
        return 2

    root = Path("governance/execpolicy")
    try:
        rules = load_profile_rules(root, args.profile)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    if args.command:
        verdict = classify_command(rules, args.command)
        target = args.command
        kind = "command"
    else:
        verdict = classify_path(rules, args.action or "read", args.path or "")
        target = args.path or ""
        kind = args.action or "read"

    mode = "dry-run" if args.dry_run or True else "enforce"
    print(f"[{mode}] profile={args.profile} {kind}={target!r} -> {verdict}")
    if verdict in {"deny", "prompt"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
