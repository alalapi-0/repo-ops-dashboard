#!/usr/bin/env python3
"""Read and summarize scan_policy.yaml."""

from __future__ import annotations

import json
from pathlib import Path

from validate_scan_policy import read_scan_policy, summarize_scan_policy, validate_scan_policy  # noqa: E402


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Read and summarize scan_policy.yaml")
    parser.add_argument("path", nargs="?", default="config/scan_policy.yaml")
    parser.add_argument("--json", action="store_true", help="Print summary as JSON")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        data = read_scan_policy(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}")
        return 1

    errors = validate_scan_policy(data, path.name)
    if errors:
        print(f"[invalid] {errors[0]}")
        return 1

    summary = summarize_scan_policy(data)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print(f"scanner_version: {summary['scanner_version']}")
    print(f"core_categories: {', '.join(summary['core_categories'])}")
    print(f"required_categories: {', '.join(summary['required_categories'])}")
    print(f"pattern_count: {summary['pattern_count']}")
    print(f"default_dry_run: {summary['default_dry_run']}")
    print(f"max_file_kb: {summary['max_file_kb']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
