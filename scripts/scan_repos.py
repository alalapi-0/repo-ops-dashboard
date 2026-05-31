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


IGNORED_DIR_ENTRIES = {".git", ".DS_Store"}


def is_repository_empty(repo_path: Path) -> bool:
    for child in repo_path.iterdir():
        if child.name in IGNORED_DIR_ENTRIES:
            continue
        return False
    return True


def collect_files(
    repo_path: Path,
    patterns: list[str],
    denylist: list[str],
    max_file_bytes: int,
) -> tuple[list[str], list[str], list[str], list[str]]:
    read_files: list[str] = []
    missing: list[str] = []
    skipped: list[str] = []
    warnings: list[str] = []

    for pattern in patterns:
        if is_denied(pattern, denylist):
            skipped.append(f"denied pattern: {pattern}")
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
                    skipped.append(f"denied file: {rel}")
                    continue
                try:
                    size = match.stat().st_size
                except OSError as exc:
                    warnings.append(f"stat failed: {rel} ({exc})")
                    continue
                if size > max_file_bytes:
                    warnings.append(f"file too large ({size} bytes): {rel}")
                    continue
                read_files.append(rel)
        else:
            candidate = repo_path / pattern
            if candidate.is_file():
                rel = candidate.relative_to(repo_path).as_posix()
                if is_denied(rel, denylist):
                    skipped.append(f"denied file: {rel}")
                    continue
                try:
                    size = candidate.stat().st_size
                except OSError as exc:
                    warnings.append(f"stat failed: {rel} ({exc})")
                    continue
                if size > max_file_bytes:
                    warnings.append(f"file too large ({size} bytes): {rel}")
                    continue
                read_files.append(rel)
            elif candidate.exists() and candidate.is_dir():
                warnings.append(f"skip directory target: {pattern}")
            else:
                missing.append(pattern)

    dedup = sorted(set(read_files))
    return dedup, missing, skipped, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read only scan managed repository files")
    parser.add_argument("--config", default="config/repos.example.yaml", help="Repo config yaml path")
    parser.add_argument("--managed-files", default="config/managed_files.yaml", help="Managed files policy yaml path")
    parser.add_argument("--output", default="data/repo_snapshots.json", help="Output json path")
    parser.add_argument(
        "--max-file-kb",
        type=int,
        default=512,
        help="Skip files larger than this size in KB (default 512)",
    )
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
            "priority_hint": str(repo.get("priority_hint", "")),
            "exists": path.exists(),
            "read_files": [],
            "missing": [],
            "skipped": [],
            "warnings": [],
        }

        if not path.exists():
            row["status"] = "missing"
            row["missing"].append("repository path missing")
            result["repos"].append(row)
            print(f"[missing] {name}: {path}")
            continue

        if not path.is_dir():
            row["status"] = "missing"
            row["missing"].append("repository path is not a directory")
            result["repos"].append(row)
            print(f"[missing] {name}: not a directory")
            continue

        if is_repository_empty(path):
            row["status"] = "empty"
            row["warnings"].append("repository directory empty")
            result["repos"].append(row)
            print(f"[empty] {name}: {path}")
            continue

        patterns = normalize_patterns(repo.get("managed_files"), global_allowlist)
        max_file_bytes = max(int(args.max_file_kb), 1) * 1024
        read_files, missing, skipped, warnings = collect_files(path, patterns, denylist, max_file_bytes)
        row["read_files"] = read_files
        row["missing"] = missing
        row["skipped"] = skipped
        row["warnings"] = warnings
        result["repos"].append(row)

        print(
            f"[repo] {name} read={len(read_files)} "
            f"missing={len(missing)} skipped={len(skipped)} warnings={len(warnings)}"
        )
        for file_path in read_files:
            print(f"  + {file_path}")
        for item in missing:
            print(f"  - missing: {item}")
        for item in skipped:
            print(f"  ~ skipped: {item}")
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
