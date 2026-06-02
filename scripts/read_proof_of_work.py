#!/usr/bin/env python3
"""Read and validate a single proof_of_work JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from validate_proof_of_work import read_proof_of_work, validate_proof_of_work  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read and validate a proof_of_work JSON file")
    parser.add_argument("path", help="Path to proof_of_work JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    try:
        record = read_proof_of_work(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"[error] invalid JSON: {exc}", file=sys.stderr)
        return 2

    errors = validate_proof_of_work(record, path.name)
    if errors:
        for err in errors:
            print(f"[error] {err}", file=sys.stderr)
        return 2

    print(f"[ok] proof_of_work valid: {record.get('task_id')}")
    if args.pretty:
        print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
