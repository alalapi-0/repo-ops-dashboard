#!/usr/bin/env python3
"""Extract playbook/skill candidates from proof_of_work_registry (dry-run default)."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

DEFAULT_POLICY = "config/playbook_extraction_policy.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


def dump_registry(path: Path, data: dict[str, Any]) -> None:
    header = (
        "# Playbook / skill candidates (Personal Agent OS).\n"
        "# Sources: proof_of_work_registry via scripts/extract_playbook_candidates.py\n"
    )
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def slug_task_id(task_id: str) -> str:
    return task_id.replace("task_", "").replace("-", "_")


def record_eligible(record: dict[str, Any], selection: dict[str, Any]) -> bool:
    status = str(record.get("status", "")).lower()
    allowlist = {str(s).lower() for s in selection.get("status_allowlist", [])}
    if status not in allowlist:
        return False
    if selection.get("require_tests_passed") and record.get("tests_passed") is not True:
        return False
    max_issues = selection.get("max_known_issues")
    if max_issues is not None:
        issue_count = int(record.get("known_issue_count", 0))
        if issue_count > int(max_issues):
            return False
    return True


def build_candidate(record: dict[str, Any], defaults: dict[str, Any], *, now: str) -> dict[str, Any]:
    task_id = str(record.get("task_id", "unknown"))
    project_id = str(record.get("project_id", "unknown"))
    slug = slug_task_id(task_id)
    return {
        "candidate_id": f"playbook_{slug}",
        "kind": "playbook",
        "status": str(defaults.get("status", "proposed")),
        "lifecycle": str(defaults.get("lifecycle", "candidate")),
        "approval": str(defaults.get("approval", "human_required")),
        "project_id": project_id,
        "source_task_id": task_id,
        "proof_path": record.get("proof_path"),
        "summary": record.get("summary") or f"Candidate from completed task {task_id}",
        "context_refs": [
            str(record.get("proof_path", "")),
            "governance/playbooks/",
        ],
        "extracted_at": now,
    }


def render_report(candidates: list[dict[str, Any]], *, dry_run: bool) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Playbook Candidate Extraction",
        "",
        f"- generated_at: {ts}",
        f"- candidate_count: {len(candidates)}",
        f"- mode: {'dry-run' if dry_run else 'write'}",
        "",
    ]
    for row in candidates:
        lines.append(f"- {row.get('candidate_id')}: {row.get('source_task_id')} ({row.get('project_id')})")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract playbook candidates from proof_of_work")
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    policy_path = root / args.policy
    if not policy_path.exists():
        print(f"[playbook_candidates] policy missing: {policy_path}")
        return 2

    from validate_playbook_extraction_policy import validate_playbook_extraction_policy

    policy = load_yaml(policy_path)
    errors = validate_playbook_extraction_policy(policy, source=policy_path.name)
    if errors:
        print(f"[playbook_candidates] policy invalid: {errors[:3]}")
        return 2

    sources = policy.get("sources", {})
    registry_path = root / str(sources.get("proof_of_work_registry", "governance/proof_of_work_registry.yaml"))
    if not registry_path.exists():
        print(f"[playbook_candidates] registry missing: {registry_path}")
        return 2

    registry = load_yaml(registry_path)
    records = list(registry.get("records", []))
    selection = policy.get("selection", {})
    defaults = policy.get("candidate_defaults", {})
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    candidates = [
        build_candidate(record, defaults, now=now)
        for record in records
        if isinstance(record, dict) and record_eligible(record, selection)
    ]
    candidates.sort(key=lambda row: str(row.get("candidate_id", "")))

    dry_run = not args.write and bool(policy.get("defaults", {}).get("dry_run", True))
    report_path = root / str(sources.get("report", "reports/playbook_candidates_extraction.md"))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(candidates, dry_run=dry_run), encoding="utf-8")

    payload = {
        "schema_version": "0.1.0",
        "generated_at": now,
        "source_registry": registry_path.relative_to(root).as_posix(),
        "summary": {
            "total_candidates": len(candidates),
            "auto_approve": bool(policy.get("defaults", {}).get("auto_approve", True)),
        },
        "candidates": candidates,
    }

    if dry_run:
        print(f"[playbook_candidates] dry-run extracted={len(candidates)} report={report_path.name}")
        return 0

    output_path = root / str(sources.get("output", "governance/playbook_candidates.yaml"))
    dump_registry(output_path, payload)
    print(f"[playbook_candidates] wrote {output_path.relative_to(root)} count={len(candidates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
