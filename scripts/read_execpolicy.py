#!/usr/bin/env python3
"""Read and summarize governance/execpolicy rules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from validate_execpolicy import (  # noqa: E402
    KNOWN_PROFILES,
    read_execpolicy_file,
    summarize_execpolicy,
    validate_execpolicy_dir,
    validate_execpolicy_file,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read and validate execpolicy rules")
    parser.add_argument("path", nargs="?", help="Path to a .rules file")
    parser.add_argument("--profile", choices=list(KNOWN_PROFILES), help="Load a named profile")
    parser.add_argument("--all", action="store_true", help="Validate governance/execpolicy/")
    parser.add_argument("--json", action="store_true", help="Output summary as JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path("governance/execpolicy")

    if args.all:
        errors = validate_execpolicy_dir(root)
        if errors:
            print(f"[invalid] {errors[0]}", file=sys.stderr)
            for err in errors[1:5]:
                print(f"  - {err}", file=sys.stderr)
            return 1
        portfolio_rules, _ = read_execpolicy_file(root / "portfolio.rules")
        summary = summarize_execpolicy(portfolio_rules)
        summary["profiles"] = list(KNOWN_PROFILES)
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(f"[ok] execpolicy valid: {summary['total_rules']} portfolio rules, {len(KNOWN_PROFILES)} profiles")
        return 0

    if args.profile:
        profile_path = root / "profiles" / f"{args.profile}.rules"
        rules, parse_errors = read_execpolicy_file(profile_path)
        errors = parse_errors + validate_execpolicy_file(profile_path)
    elif args.path:
        path = Path(args.path)
        rules, parse_errors = read_execpolicy_file(path)
        required = None
        if path.name == "portfolio.rules":
            from validate_execpolicy import REQUIRED_PORTFOLIO_CHECKS

            required = REQUIRED_PORTFOLIO_CHECKS
        errors = parse_errors + validate_execpolicy_file(path, required=required)
    else:
        print("[error] specify path, --profile, or --all", file=sys.stderr)
        return 2

    if errors:
        print(f"[invalid] {errors[0]}", file=sys.stderr)
        return 1

    summary = summarize_execpolicy(rules)
    if args.json:
        payload = {
            **summary,
            "rules": [
                {"action": rule.action, "kind": rule.kind, "pattern": rule.pattern, "line": rule.line_no}
                for rule in rules
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        label = args.profile or Path(args.path).name if args.path else "execpolicy"
        print(f"[ok] {label}: {summary['total_rules']} rules (allow={summary['allow']}, deny={summary['deny']}, prompt={summary['prompt']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
