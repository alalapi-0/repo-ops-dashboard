#!/usr/bin/env python3
"""Generate a handoff_packet YAML from a governance task_spec (dry-run by default)."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

DEFAULT_TEMPLATE = "governance/handoffs/handoff_packet.template.yaml"
DEFAULT_OUTPUT_DIR = "governance/handoffs/generated"
DEFAULT_TRACKING = "governance/handoffs/tracking.yaml"

AGENT_PROFILE = {
    "Cursor": "repo_ops_guarded",
    "Codex": "readonly_managed_repo",
    "OpenClaw": "readonly_managed_repo",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected mapping: {path}")
    return data


def build_packet(spec: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    task_id = str(spec.get("task_id", "unknown"))
    agent = str(spec.get("assigned_agent", "Cursor")).strip() or "Cursor"
    handoff_id = f"handoff_{task_id.replace('task_', '')}"
    wd = str(spec.get("working_directory", "")).strip() or str(repo_root)
    refs = list(spec.get("reference_paths") or [])
    refs.extend(
        [
            "docs/handoff_protocol.md",
            f"governance/task_specs/{task_id}.yaml",
        ]
    )
    return {
        "handoff_id": handoff_id,
        "parent_task_id": task_id,
        "target_agent": agent,
        "working_directory": wd,
        "task_spec_path": f"governance/task_specs/{Path(task_id).name}.yaml",
        "context_refs": sorted({str(r) for r in refs if r}),
        "allowed_files": list(spec.get("scope") or ["governance/**"]),
        "denied_files": [
            "**/.env",
            "**/.env.*",
            "managed_repos/**",
        ],
        "confirmation_policy": str(spec.get("confirmation_policy", "human_review_before_execution")),
        "execpolicy_profile": str(spec.get("execpolicy_profile", AGENT_PROFILE.get(agent, "readonly_managed_repo"))),
        "expected_artifacts": list(spec.get("artifacts_expected") or []),
        "timeout": "24h",
        "return_contract": {
            "proof_of_work_path": f"governance/proof_of_work/{task_id}_pow.json",
            "validation_commands": list(spec.get("validation_commands") or ["python3 scripts/agent_gate.py"]),
            "status_field": "status",
            "allowed_return_statuses": ["completed", "blocked", "needs_review"],
        },
    }


def append_tracking(
    tracking_path: Path,
    packet: dict[str, Any],
    packet_rel: str,
    *,
    dry_run: bool,
) -> None:
    tracking = load_yaml(tracking_path) if tracking_path.exists() else {"schema_version": "0.1.0", "items": []}
    items = list(tracking.get("items", []))
    handoff_id = str(packet["handoff_id"])
    if any(str(i.get("handoff_id")) == handoff_id for i in items if isinstance(i, dict)):
        return
    items.append(
        {
            "handoff_id": handoff_id,
            "parent_task_id": packet["parent_task_id"],
            "target_agent": packet["target_agent"],
            "status": "dispatched" if not dry_run else "proposed",
            "dispatched_at": datetime.now(timezone.utc).isoformat(),
            "packet_path": packet_rel,
            "return_status": "pending",
            "return_received_at": None,
            "proof_of_work_path": None,
            "notes": "auto-generated (dry-run)" if dry_run else "auto-generated",
        }
    )
    tracking["items"] = items
    tracking["updated_at"] = datetime.now(timezone.utc).isoformat()
    if not dry_run:
        tracking_path.parent.mkdir(parents=True, exist_ok=True)
        with tracking_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(tracking, handle, sort_keys=False, allow_unicode=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate handoff_packet from task_spec")
    parser.add_argument("--task-spec", required=True, help="Path to task_spec YAML")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--tracking", default=DEFAULT_TRACKING)
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--write", action="store_true", help="Write packet and update tracking")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    spec_path = root / args.task_spec
    spec = load_yaml(spec_path)
    packet = build_packet(spec, repo_root=root)

    out_dir = root / args.output_dir
    out_path = out_dir / f"{packet['handoff_id']}.yaml"
    rel = str(out_path.relative_to(root))

    dry_run = args.dry_run and not args.write
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(packet, handle, sort_keys=False, allow_unicode=True)
        append_tracking(root / args.tracking, packet, rel, dry_run=False)
    else:
        append_tracking(root / args.tracking, packet, rel, dry_run=True)

    errors = __import__("validate_handoff_packet", fromlist=["validate_handoff_packet"]).validate_handoff_packet(
        packet, source="generated"
    )
    if errors:
        print(f"[handoff] validation errors: {errors}")
        return 2

    print(f"[handoff] id={packet['handoff_id']} agent={packet['target_agent']} dry_run={dry_run}")
    if not dry_run:
        print(f"[handoff] wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
