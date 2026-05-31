#!/usr/bin/env python3
"""Read-only repository scanner for management files."""

from __future__ import annotations

import argparse
import fnmatch
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def is_denied(path_text: str, denylist: list[str]) -> bool:
    return any(fnmatch.fnmatch(path_text, pattern) for pattern in denylist)


def normalize_patterns(patterns: list[str] | None, fallback: list[str]) -> list[str]:
    return list(patterns) if patterns else list(fallback)


def collect_files(repo_path: Path, patterns: list[str], denylist: list[str]) -> tuple[list[str], list[str]]:
    read_files: list[str] = []
    warnings: list[str] = []

    for pattern in patterns:
        if is_denied(pattern, denylist):
            warnings.append(f"skip denied pattern: {pattern}")
            continue

        if any(token in pattern for token in ["*", "?", "["]):
            matches = list(repo_path.glob(pattern))
            if not matches:
                warnings.append(f"pattern no match: {pattern}")
            for match in matches:
                if not match.is_file():
                    continue
                rel = match.relative_to(repo_path).as_posix()
                if is_denied(rel, denylist):
                    warnings.append(f"skip denied file: {rel}")
                    continue
                read_files.append(rel)
        else:
            candidate = repo_path / pattern
            if candidate.is_file():
                rel = candidate.relative_to(repo_path).as_posix()
                if is_denied(rel, denylist):
                    warnings.append(f"skip denied file: {rel}")
                    continue
                read_files.append(rel)
            elif candidate.exists() and candidate.is_dir():
                warnings.append(f"skip directory target: {pattern}")
            else:
                warnings.append(f"missing file: {pattern}")

    dedup = sorted(set(read_files))
    return dedup, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read only scan managed repository files")
    parser.add_argument("--config", default="config/repos.example.yaml", help="Repo config yaml path")
    parser.add_argument("--managed-files", default="config/managed_files.yaml", help="Managed files policy yaml path")
    parser.add_argument("--output", default="data/repo_snapshots.json", help="Output json path")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Default true: print only")
    parser.add_argument("--no-dry-run", action="store_false", dest="dry_run", help="Write output file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    policy_path = Path(args.managed_files)

    if not config_path.exists():
        raise SystemExit(f"Config not found: {config_path}")
    if not policy_path.exists():
        raise SystemExit(f"Managed files policy not found: {policy_path}")

    repo_cfg = load_yaml(config_path)
    policy_cfg = load_yaml(policy_path)

    global_allowlist = list(policy_cfg.get("allowlist", []))
    denylist = list(policy_cfg.get("denylist", []))
    repos = list(repo_cfg.get("repos", []))

    result: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "repos": [],
    }

    print(f"[scan] repos={len(repos)} dry_run={args.dry_run}")
    for repo in repos:
        name = str(repo.get("name", "unknown"))
        path = Path(str(repo.get("path", "")))
        status_hint = str(repo.get("status_hint", "unknown"))
        repo_type = str(repo.get("type", "unknown"))

        row: dict[str, Any] = {
            "name": name,
            "path": path.as_posix(),
            "type": repo_type,
            "status": status_hint,
            "exists": path.exists(),
            "read_files": [],
            "warnings": [],
        }

        if not path.exists():
            row["status"] = "missing"
            row["warnings"].append("repository path missing")
            result["repos"].append(row)
            print(f"[missing] {name}: {path}")
            continue

        if not path.is_dir():
            row["status"] = "missing"
            row["warnings"].append("repository path is not a directory")
            result["repos"].append(row)
            print(f"[missing] {name}: not a directory")
            continue

        patterns = normalize_patterns(repo.get("managed_files"), global_allowlist)
        read_files, warnings = collect_files(path, patterns, denylist)
        row["read_files"] = read_files
        row["warnings"] = warnings
        result["repos"].append(row)

        print(f"[repo] {name} read={len(read_files)} warnings={len(warnings)}")
        for file_path in read_files:
            print(f"  + {file_path}")
        for warn in warnings:
            print(f"  ! {warn}")

    if args.dry_run:
        print("[dry-run] output file not written")
        return 0

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] wrote snapshots: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
