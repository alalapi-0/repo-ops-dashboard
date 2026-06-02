#!/usr/bin/env python3
"""Build governance/portfolio_state.yaml from project_registry and repo status JSON."""

from __future__ import annotations

import argparse
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


def load_json(path: Path) -> dict[str, Any]:
    import json

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_state(path: Path, data: dict[str, Any]) -> None:
    header = (
        "# Portfolio state snapshot (Personal Agent OS).\n"
        "# Sources: governance/project_registry.yaml + repo status JSON\n"
    )
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def health_band(score: int | None) -> str:
    if score is None:
        return "unknown"
    if score >= 70:
        return "green"
    if score >= 40:
        return "yellow"
    return "red"


def count_open_reviews(root: Path) -> int:
    queue = load_yaml(root / "governance" / "review_queue.yaml")
    items = list(queue.get("items", []))
    open_status = {"pending", "open", "awaiting_human"}
    return sum(1 for item in items if str(item.get("status", "")).lower() in open_status)


def status_index(status_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(repo.get("name", "")): repo for repo in status_payload.get("repos", [])}


def build_project_state(registry_project: dict[str, Any], repo_row: dict[str, Any] | None) -> dict[str, Any]:
    project_id = str(registry_project.get("project_id", ""))
    lifecycle = str(registry_project.get("lifecycle", "active"))
    if repo_row:
        lifecycle = str(repo_row.get("lifecycle_status") or repo_row.get("status") or lifecycle)
        blockers = list(repo_row.get("blockers") or [])
        next_actions = list(repo_row.get("next_actions") or [])
        priority = str(repo_row.get("priority") or registry_project.get("priority_hint", "medium"))
        agent = str(repo_row.get("recommended_agent") or registry_project.get("default_agent", "Cursor"))
        score = repo_row.get("health_score")
        if isinstance(score, (int, float)):
            health = health_band(int(score))
        else:
            health = "unknown"
        last_checked = repo_row.get("last_checked")
    else:
        blockers = []
        next_actions = ["Run scan_repos.py and refresh status snapshot"]
        priority = str(registry_project.get("priority_hint", "medium"))
        agent = str(registry_project.get("default_agent", "Cursor"))
        health = "unknown"
        last_checked = None

    state: dict[str, Any] = {
        "project_id": project_id,
        "repo_name": registry_project.get("repo_name"),
        "lifecycle": lifecycle,
        "health": health,
        "priority": priority,
        "recommended_agent": agent,
        "current_task_id": None,
        "blockers": blockers,
        "next_actions": next_actions,
    }
    if last_checked:
        state["last_checked"] = last_checked
    if repo_row and repo_row.get("priority_score") is not None:
        state["priority_score"] = int(repo_row["priority_score"])
    return state


def build_summary(projects: list[dict[str, Any]], review_open: int, *, budget_warning: bool = False) -> dict[str, Any]:
    active = sum(
        1
        for p in projects
        if str(p.get("lifecycle", "")) in {"active", "bootstrap", "maintenance", "idea"}
    )
    blocked = sum(1 for p in projects if p.get("blockers"))
    wip = sum(1 for p in projects if p.get("current_task_id"))
    return {
        "total_projects": len(projects),
        "active_projects": active,
        "blocked_projects": blocked,
        "review_queue_open": review_open,
        "current_wip": wip,
        "budget_warning": budget_warning,
    }


def budget_warning_from_tracking(root: Path) -> bool:
    path = root / "governance" / "budget_cost_tracking.yaml"
    if not path.exists():
        return False
    data = load_yaml(path)
    summary = data.get("summary", {})
    return bool(summary.get("portfolio_budget_warning"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync governance/portfolio_state.yaml")
    parser.add_argument("--registry", default="governance/project_registry.yaml")
    parser.add_argument("--status", default="data/repo_status.example.json")
    parser.add_argument("--output", default="governance/portfolio_state.yaml")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    registry_path = Path(args.registry)
    status_path = Path(args.status)
    output_path = Path(args.output)

    if not registry_path.exists():
        raise SystemExit(f"Registry not found: {registry_path}")
    if not status_path.exists():
        raise SystemExit(f"Status input not found: {status_path}")

    registry = load_yaml(registry_path)
    status_payload = load_json(status_path)
    by_name = status_index(status_payload)
    projects = [
        build_project_state(entry, by_name.get(str(entry.get("repo_name", ""))))
        for entry in registry.get("projects", [])
    ]
    review_open = count_open_reviews(root)
    budget_warn = budget_warning_from_tracking(root)
    payload = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status_source": str(status_path.as_posix()),
        "registry_source": str(registry_path.as_posix()),
        "summary": build_summary(projects, review_open, budget_warning=budget_warn),
        "projects": projects,
    }

    print(
        f"[ok] portfolio snapshot: {len(projects)} projects, "
        f"blocked={payload['summary']['blocked_projects']}, review_open={review_open}"
    )
    if args.dry_run:
        print("[dry-run] file not written")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dump_state(output_path, payload)
    print(f"[ok] wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
