#!/usr/bin/env python3
"""Build governance/project_registry.yaml from config/repos.yaml (read-only source)."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

REQUIRED_PROJECT_FIELDS = (
    "project_id",
    "repo_name",
    "path",
    "domain",
    "lifecycle",
    "owner",
    "default_agent",
    "governance_level",
)

AGENT_BY_TYPE: dict[str, str] = {
    "meta_ops": "Cursor",
    "novel_agent": "Codex",
    "ai_manga": "Codex",
    "ai_anime": "Codex",
    "content_scheduler": "Codex",
    "translation": "Codex",
    "study": "Cursor",
    "news": "Cursor",
    "asset_forge": "Codex",
    "experiment": "Cursor",
    "external": "Human",
    "lab": "Cursor",
    "utility": "Cursor",
}

DOMAIN_BY_TYPE: dict[str, str] = {
    "meta_ops": "portfolio_governance",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def dump_registry(path: Path, data: dict[str, Any]) -> None:
    header = (
        "# Machine-readable project registry (Personal Agent OS).\n"
        "# Source: config/repos.yaml via scripts/sync_project_registry.py\n"
        "# Do not hand-edit paths; re-run sync after repos.yaml changes.\n"
    )
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def project_id_from_name(name: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    return normalized or "unknown_project"


def lifecycle_from_hint(status_hint: str, repo_name: str) -> str:
    if status_hint in {"bootstrap", "active", "paused", "archived", "frozen"}:
        return status_hint
    return "bootstrap" if repo_name == "repo-ops-dashboard" else "active"


def default_agent(repo_type: str, repo_name: str) -> str:
    if repo_name == "repo-ops-dashboard":
        return "Cursor"
    return AGENT_BY_TYPE.get(repo_type, "Cursor")


def governance_level(repo_name: str) -> str:
    return "write_allowed" if repo_name == "repo-ops-dashboard" else "readonly_managed_repo"


def domain_for(repo_type: str) -> str:
    return DOMAIN_BY_TYPE.get(repo_type, repo_type)


def build_project(entry: dict[str, Any]) -> dict[str, Any]:
    name = str(entry.get("name", "")).strip()
    path = str(entry.get("path", "")).strip()
    repo_type = str(entry.get("type", "utility"))
    status_hint = str(entry.get("status_hint", "active"))
    priority_hint = str(entry.get("priority_hint", "medium"))
    project: dict[str, Any] = {
        "project_id": project_id_from_name(name),
        "repo_name": name,
        "path": path,
        "domain": domain_for(repo_type),
        "lifecycle": lifecycle_from_hint(status_hint, name),
        "owner": "HumanOwner",
        "default_agent": default_agent(repo_type, name),
        "governance_level": governance_level(name),
        "priority_hint": priority_hint,
        "registry_source": "config/repos.yaml",
    }
    if name == "repo-ops-dashboard":
        project["context_index_path"] = "repo_context_index.yaml"
        project["key_files"] = [
            "README.md",
            "AGENTS.md",
            "repo_protocol_standard.yaml",
            "round_state/current_round.yaml",
        ]
        project["notes"] = "Personal Agent OS governance layer itself."
    return project


def validate_projects(projects: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for idx, project in enumerate(projects):
        pid = str(project.get("project_id", ""))
        if pid in seen:
            errors.append(f"duplicate project_id: {pid}")
        seen.add(pid)
        missing = [field for field in REQUIRED_PROJECT_FIELDS if not project.get(field)]
        if missing:
            errors.append(f"project[{idx}] ({pid or '?'}) missing: {missing}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync governance/project_registry.yaml from repos.yaml")
    parser.add_argument("--input", default="config/repos.yaml", help="Source repos registry")
    parser.add_argument("--output", default="governance/project_registry.yaml", help="Output registry path")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print summary without writing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    repos_cfg = load_yaml(input_path)
    repos = list(repos_cfg.get("repos", []))
    if not repos:
        raise SystemExit(f"No repos in {input_path}")

    projects = [build_project(entry) for entry in repos]
    errors = validate_projects(projects)
    if errors:
        for err in errors:
            print(f"[error] {err}")
        return 2

    payload = {
        "schema_version": "0.1.0",
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": str(input_path.as_posix()),
        "project_count": len(projects),
        "projects": projects,
    }

    print(f"[ok] {len(projects)} project(s) ready from {input_path}")
    if args.dry_run:
        print("[dry-run] file not written")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dump_registry(output_path, payload)
    print(f"[ok] wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
