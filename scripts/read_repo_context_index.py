#!/usr/bin/env python3
"""Read and validate repo_context_index.yaml."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from validate_repo_context_index import (  # noqa: E402
    read_repo_context_index,
    summarize_repo_context_index,
    validate_repo_context_index,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read and validate repo_context_index.yaml")
    parser.add_argument("path", nargs="?", default="repo_context_index.yaml")
    parser.add_argument("--json", action="store_true", help="Output summary as JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    try:
        data = read_repo_context_index(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    errors = validate_repo_context_index(data, path.name)
    if errors:
        print(f"[invalid] {errors[0]}", file=sys.stderr)
        return 1

    summary = summarize_repo_context_index(data)
    if args.json:
        print(json.dumps({"path": str(path), **summary, "summary_text": data.get("summary")}, ensure_ascii=False, indent=2))
    else:
        print(
            f"[ok] {path.name}: project_id={summary['project_id']} "
            f"stage={summary['current_stage']} key_files={summary['key_files_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
