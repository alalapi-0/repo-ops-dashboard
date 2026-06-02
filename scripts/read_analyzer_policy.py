#!/usr/bin/env python3
"""Read and summarize analyzer_policy.yaml."""

from __future__ import annotations

import json
from pathlib import Path

from validate_analyzer_policy import read_analyzer_policy, summarize_analyzer_policy, validate_analyzer_policy  # noqa: E402


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Read and summarize analyzer_policy.yaml")
    parser.add_argument("path", nargs="?", default="config/analyzer_policy.yaml")
    parser.add_argument("--json", action="store_true", help="Print summary as JSON")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        data = read_analyzer_policy(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}")
        return 1

    errors = validate_analyzer_policy(data, path.name)
    if errors:
        print(f"[invalid] {errors[0]}")
        return 1

    summary = summarize_analyzer_policy(data)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print(f"analyzer_version: {summary['analyzer_version']}")
    print(f"dimensions: {', '.join(summary['dimensions'])}")
    print(f"total_weight: {summary['total_weight']}")
    print(f"registry_path: {summary['registry_path']}")
    print(f"round_state_file: {summary['round_state_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
