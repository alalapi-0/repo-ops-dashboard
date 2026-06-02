#!/usr/bin/env python3
"""Read and validate a single governance task_spec YAML file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sync_governance_task_queue import read_task_spec, validate_task_spec  # noqa: E402

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read and validate a task_spec YAML file")
    parser.add_argument("path", help="Path to task_spec YAML")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    try:
        spec = read_task_spec(path)
    except FileNotFoundError:
        print(f"[error] not found: {path}", file=sys.stderr)
        return 1

    errors = validate_task_spec(spec, path.name)
    if errors:
        for err in errors:
            print(f"[error] {err}", file=sys.stderr)
        return 2

    print(f"[ok] task_spec valid: {spec.get('task_id')}")
    if args.json:
        print(json.dumps(spec, ensure_ascii=False, indent=2))
    else:
        print(yaml.safe_dump(spec, allow_unicode=True, sort_keys=False, default_flow_style=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
