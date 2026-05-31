#!/usr/bin/env python3
"""Merge new workspace subdirectories into config/repos.yaml without overwriting existing hints."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

SKIP_NAMES = {".git", ".DS_Store"}

HIGH_NAMES = {
    "novel-continuation-agent",
    "ai-manga",
    "repo-ops-dashboard",
    "ai-anime-short-factory",
    "wechat-article-scheduler",
}

MEDIUM_NAMES = {
    "light_novel",
    "computer_study_plan",
    "world-news-lens",
    "pixel-world-asset-forge",
}

TYPE_BY_NAME: dict[str, str] = {
    "novel-continuation-agent": "novel_agent",
    "ai-manga": "ai_manga",
    "repo-ops-dashboard": "meta_ops",
    "ai-anime-short-factory": "ai_anime",
    "wechat-article-scheduler": "content_scheduler",
    "light_novel": "translation",
    "computer_study_plan": "study",
    "world-news-lens": "news",
    "pixel-world-asset-forge": "asset_forge",
}


def default_type(name: str) -> str:
    if name in TYPE_BY_NAME:
        return TYPE_BY_NAME[name]
    if "lab" in name or name.endswith("-labs"):
        return "lab"
    if name.endswith("-external"):
        return "external"
    if "experiment" in name:
        return "experiment"
    return "utility"


def default_priority(name: str) -> str:
    if name in HIGH_NAMES:
        return "high"
    if name in MEDIUM_NAMES:
        return "medium"
    return "low"


def default_status_hint(name: str) -> str:
    return "bootstrap" if name == "repo-ops-dashboard" else "active"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def dump_yaml(path: Path, data: dict[str, Any]) -> None:
    header = (
        "# Real registry: one subdirectory under PycharmProjects = one repo.\n"
        "# Run: python3 scripts/sync_repo_registry.py --workspace /Users/alalapi/PycharmProjects\n"
    )
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def list_workspace_dirs(workspace: Path) -> list[str]:
    names: list[str] = []
    for child in sorted(workspace.iterdir()):
        if not child.is_dir():
            continue
        if child.name in SKIP_NAMES or child.name.startswith("."):
            continue
        names.append(child.name)
    return names


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync repos.yaml from workspace subdirectories")
    parser.add_argument(
        "--workspace",
        default="/Users/alalapi/PycharmProjects",
        help="Parent directory containing project folders",
    )
    parser.add_argument(
        "--output",
        default="config/repos.yaml",
        help="Registry yaml path to update",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned additions only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace)
    output_path = Path(args.output)

    if not workspace.is_dir():
        raise SystemExit(f"Workspace not found: {workspace}")

    cfg = load_yaml(output_path) if output_path.exists() else {"repos": []}
    repos: list[dict[str, Any]] = list(cfg.get("repos", []))
    by_name = {str(r.get("name")): r for r in repos}

    added = 0
    for name in list_workspace_dirs(workspace):
        if name in by_name:
            continue
        path = (workspace / name).resolve().as_posix()
        entry = {
            "name": name,
            "path": path,
            "type": default_type(name),
            "priority_hint": default_priority(name),
            "status_hint": default_status_hint(name),
        }
        repos.append(entry)
        by_name[name] = entry
        added += 1
        print(f"[add] {name} -> {path}")

    if added == 0:
        print("[ok] no new directories to add")
        return 0

    if args.dry_run:
        print(f"[dry-run] would append {added} repo(s); file not written")
        return 0

    dump_yaml(output_path, {"repos": repos})
    print(f"[ok] wrote {output_path} (+{added} repo(s), total={len(repos)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
