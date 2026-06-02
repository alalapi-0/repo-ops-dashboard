#!/usr/bin/env python3
"""Read and summarize priority_scoring_policy.yaml."""

from __future__ import annotations

import json
from pathlib import Path

from validate_priority_scoring_policy import (  # noqa: E402
    read_priority_scoring_policy,
    summarize_priority_scoring_policy,
    validate_priority_scoring_policy,
)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Read and summarize priority_scoring_policy.yaml")
    parser.add_argument("path", nargs="?", default="config/priority_scoring_policy.yaml")
    parser.add_argument("--json", action="store_true", help="Print summary as JSON")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        data = read_priority_scoring_policy(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}")
        return 1

    errors = validate_priority_scoring_policy(data, path.name)
    if errors:
        print(f"[invalid] {errors[0]}")
        return 1

    summary = summarize_priority_scoring_policy(data)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print(f"scoring_version: {summary['scoring_version']}")
    print(f"factors: {', '.join(summary['factors'])}")
    print(f"product_scale: {summary['product_scale']}")
    print(f"expression: {summary['expression']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
