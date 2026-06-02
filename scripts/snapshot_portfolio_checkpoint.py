#!/usr/bin/env python3
"""Write portfolio_state checkpoint YAML under governance/checkpoints (dry-run default)."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

DEFAULT_POLICY = "config/checkpoint_snapshot_policy.yaml"
DEFAULT_REPORT = "reports/portfolio_checkpoint_snapshot.md"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


def dump_yaml(path: Path, data: dict[str, Any], header: str) -> None:
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def slug_timestamp(ts: datetime) -> str:
    return ts.strftime("%Y%m%dT%H%M%SZ")


def build_checkpoint_id(prefix: str, ts: datetime) -> str:
    base = prefix.rstrip("_")
    return f"{base}_{slug_timestamp(ts)}"


def prune_entries(entries: list[dict[str, Any]], max_retained: int) -> list[dict[str, Any]]:
    ordered = sorted(entries, key=lambda row: str(row.get("created_at", "")), reverse=True)
    return ordered[:max_retained]


def render_report(
    *,
    checkpoint_id: str,
    snapshot_path: str,
    project_count: int,
    dry_run: bool,
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    mode = "dry-run" if dry_run else "write"
    return "\n".join(
        [
            "# Portfolio Checkpoint Snapshot",
            "",
            f"- generated_at: {ts}",
            f"- checkpoint_id: {checkpoint_id}",
            f"- snapshot_path: {snapshot_path}",
            f"- project_count: {project_count}",
            f"- mode: {mode}",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Snapshot portfolio_state to governance/checkpoints")
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--portfolio", default=None, help="Override portfolio_state path")
    parser.add_argument("--output-report", default=DEFAULT_REPORT)
    parser.add_argument("--write", action="store_true", help="Write checkpoint files (default dry-run)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    policy_path = root / args.policy
    if not policy_path.exists():
        print(f"[checkpoint_snapshot] policy missing: {policy_path}")
        return 2

    from validate_checkpoint_snapshot_policy import validate_checkpoint_snapshot_policy

    policy = load_yaml(policy_path)
    errors = validate_checkpoint_snapshot_policy(policy, source=policy_path.name)
    if errors:
        print(f"[checkpoint_snapshot] policy invalid: {errors[:3]}")
        return 2

    snap_cfg = policy.get("snapshot", {})
    source_rel = args.portfolio or str(snap_cfg.get("source", "governance/portfolio_state.yaml"))
    source_path = root / source_rel
    if not source_path.exists():
        print(f"[checkpoint_snapshot] source missing: {source_path}")
        return 2

    portfolio = load_yaml(source_path)
    projects = list(portfolio.get("projects", []))
    if not projects:
        print("[checkpoint_snapshot] portfolio_state has no projects")
        return 2

    dry_run = not args.write and bool(policy.get("defaults", {}).get("dry_run", True))
    now = datetime.now(timezone.utc).replace(microsecond=0)
    checkpoint_id = build_checkpoint_id(str(snap_cfg.get("id_prefix", "ckpt_portfolio_")), now)
    output_dir = root / str(snap_cfg.get("output_dir", "governance/checkpoints"))
    snapshot_name = f"{checkpoint_id}.yaml"
    snapshot_rel = (output_dir / snapshot_name).relative_to(root).as_posix()

    payload = {
        "schema_version": "0.1.0",
        "checkpoint_id": checkpoint_id,
        "created_at": now.isoformat(),
        "source": source_rel,
        "portfolio_generated_at": portfolio.get("generated_at"),
        "summary": portfolio.get("summary", {}),
        "projects": projects,
    }

    manifest_rel = str(snap_cfg.get("manifest", "governance/checkpoints/manifest.yaml"))
    manifest_path = root / manifest_rel
    manifest = load_yaml(manifest_path) if manifest_path.exists() else {"schema_version": "0.1.0", "checkpoints": []}
    checkpoints = list(manifest.get("checkpoints", []))
    entry = {
        "checkpoint_id": checkpoint_id,
        "created_at": payload["created_at"],
        "path": snapshot_rel,
        "project_count": len(projects),
        "source": source_rel,
    }
    checkpoints = [row for row in checkpoints if row.get("checkpoint_id") != checkpoint_id]
    checkpoints.append(entry)
    manifest["generated_at"] = now.isoformat()
    manifest["checkpoints"] = prune_entries(checkpoints, int(snap_cfg.get("max_retained", 8)))

    report_path = root / args.output_report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_report(
            checkpoint_id=checkpoint_id,
            snapshot_path=snapshot_rel,
            project_count=len(projects),
            dry_run=dry_run,
        ),
        encoding="utf-8",
    )

    if dry_run:
        print(
            f"[checkpoint_snapshot] dry-run id={checkpoint_id} projects={len(projects)} "
            f"would_write={snapshot_rel}"
        )
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    header = (
        "# Portfolio checkpoint snapshot (Personal Agent OS).\n"
        f"# checkpoint_id: {checkpoint_id}\n"
    )
    dump_yaml(output_dir / snapshot_name, payload, header)
    dump_yaml(
        manifest_path,
        manifest,
        "# Checkpoint manifest (portfolio_state periodic snapshots).\n",
    )
    print(f"[checkpoint_snapshot] wrote {snapshot_rel} manifest={manifest_rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
