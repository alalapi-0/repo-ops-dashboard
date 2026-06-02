#!/usr/bin/env python3
"""Backup governance state — list/copy YAML assets (dry-run default, no secrets)."""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

DEFAULT_POLICY = "config/backup_restore_policy.yaml"
DEFAULT_REPORT = "reports/governance_backup_report.md"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else {}


def dump_yaml(path: Path, data: dict[str, Any]) -> None:
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(body, encoding="utf-8")


def slug_timestamp(ts: datetime) -> str:
    return ts.strftime("%Y%m%dT%H%M%SZ")


def build_backup_id(prefix: str, ts: datetime) -> str:
    return f"{prefix.rstrip('_')}_{slug_timestamp(ts)}"


def collect_paths(root: Path, rel_paths: list[str]) -> tuple[list[Path], list[str]]:
    found: list[Path] = []
    missing: list[str] = []
    for rel in rel_paths:
        path = root / rel
        if path.is_file():
            found.append(path)
        else:
            missing.append(rel)
    return found, missing


def prune_backups(entries: list[dict[str, Any]], max_retained: int) -> list[dict[str, Any]]:
    ordered = sorted(entries, key=lambda row: str(row.get("created_at", "")), reverse=True)
    return ordered[:max_retained]


def render_report(
    *,
    backup_id: str,
    files: list[str],
    missing: list[str],
    backup_dir: str,
    dry_run: bool,
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    mode = "dry-run" if dry_run else "write"
    lines = [
        "# Governance Backup Report",
        "",
        f"- generated_at: {ts}",
        f"- backup_id: {backup_id}",
        f"- mode: {mode}",
        f"- backup_dir: {backup_dir}",
        f"- file_count: {len(files)}",
        "",
        "## Included",
        "",
    ]
    for rel in files:
        lines.append(f"- {rel}")
    if missing:
        lines.extend(["", "## Missing", ""])
        for rel in missing:
            lines.append(f"- {rel}")
    lines.extend(["", "## Restore", "", "See `docs/backup_restore.md` — restore requires HITL approval.", ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backup governance state (dry-run default)")
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--output-report", default=DEFAULT_REPORT)
    parser.add_argument("--write", action="store_true", help="Copy files to governance/backups (default dry-run)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    policy = load_yaml(root / args.policy)
    backup_cfg = policy.get("backup", {})
    dry_run = not args.write

    rel_paths = [str(p) for p in backup_cfg.get("include_paths", [])]
    found, missing = collect_paths(root, rel_paths)
    ts = datetime.now(timezone.utc)
    backup_id = build_backup_id(str(backup_cfg.get("id_prefix", "backup_gov_")), ts)
    output_dir = root / str(backup_cfg.get("output_dir", "governance/backups"))
    target_dir = output_dir / backup_id

    rel_files = [p.relative_to(root).as_posix() for p in found]
    report = render_report(
        backup_id=backup_id,
        files=rel_files,
        missing=missing,
        backup_dir=target_dir.relative_to(root).as_posix(),
        dry_run=dry_run,
    )

    report_path = root / args.output_report
    if args.write:
        target_dir.mkdir(parents=True, exist_ok=True)
        for path in found:
            dest = target_dir / path.name
            shutil.copy2(path, dest)
        manifest_path = root / str(backup_cfg.get("manifest", "governance/backups/manifest.yaml"))
        manifest = load_yaml(manifest_path)
        entries = manifest.get("backups", [])
        if not isinstance(entries, list):
            entries = []
        entries.append(
            {
                "backup_id": backup_id,
                "created_at": ts.isoformat(),
                "file_count": len(found),
                "path": target_dir.relative_to(root).as_posix(),
            }
        )
        max_retained = int(backup_cfg.get("max_retained", 5))
        manifest["backups"] = prune_backups(entries, max_retained)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        dump_yaml(manifest_path, manifest)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"[backup] wrote {len(found)} files -> {target_dir}")
        print(f"[backup] manifest -> {manifest_path}")
    else:
        print(report)

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
