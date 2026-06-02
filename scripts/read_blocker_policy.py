#!/usr/bin/env python3
"""Read and summarize blocker_policy.yaml."""

from __future__ import annotations

import json
from pathlib import Path

from validate_blocker_policy import read_blocker_policy, summarize_blocker_policy, validate_blocker_policy  # noqa: E402


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Read and summarize blocker_policy.yaml")
    parser.add_argument("path", nargs="?", default="config/blocker_policy.yaml")
    parser.add_argument("--json", action="store_true", help="Print summary as JSON")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        data = read_blocker_policy(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}")
        return 1

    errors = validate_blocker_policy(data, path.name)
    if errors:
        print(f"[invalid] {errors[0]}")
        return 1

    summary = summarize_blocker_policy(data)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print(f"blocker_version: {summary['blocker_version']}")
    print(f"types: {', '.join(summary['type_ids'])}")
    print(f"escalation: {', '.join(summary['escalation_levels'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
