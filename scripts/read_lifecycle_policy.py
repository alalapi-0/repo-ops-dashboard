#!/usr/bin/env python3
"""Read and summarize lifecycle_policy.yaml."""

from __future__ import annotations

import json
from pathlib import Path

from validate_lifecycle_policy import read_lifecycle_policy, summarize_lifecycle_policy, validate_lifecycle_policy  # noqa: E402


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Read and summarize lifecycle_policy.yaml")
    parser.add_argument("path", nargs="?", default="config/lifecycle_policy.yaml")
    parser.add_argument("--json", action="store_true", help="Print summary as JSON")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        data = read_lifecycle_policy(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}")
        return 1

    errors = validate_lifecycle_policy(data, path.name)
    if errors:
        print(f"[invalid] {errors[0]}")
        return 1

    summary = summarize_lifecycle_policy(data)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print(f"lifecycle_version: {summary['lifecycle_version']}")
    print(f"states: {', '.join(summary['states'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
