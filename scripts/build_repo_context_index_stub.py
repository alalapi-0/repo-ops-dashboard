#!/usr/bin/env python3
"""Build a repo_context_index stub from project registry (stdout or governance/stubs only)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

from validate_repo_context_index import build_repo_context_index_stub, validate_repo_context_index  # noqa: E402

ALLOWLIST_README = "README.md"
THIS_REPO_ID = "repo_ops_dashboard"


def load_registry(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    projects = data.get("projects")
    if not isinstance(projects, list):
        raise ValueError("project_registry: projects must be a list")
    return projects


def first_line_summary(readme_path: Path) -> str:
    if not readme_path.is_file():
        return "Managed repository; update repo_context_index.yaml with a one-line summary."
    for line in readme_path.read_text(encoding="utf-8", errors="replace").splitlines():
        text = line.strip().lstrip("#").strip()
        if text:
            return text[:240]
    return "Managed repository; update repo_context_index.yaml with a one-line summary."


def find_project(projects: list[dict], project_id: str) -> dict:
    for project in projects:
        if str(project.get("project_id")) == project_id:
            return project
    raise KeyError(f"unknown project_id: {project_id}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build repo_context_index stub from registry")
    parser.add_argument("--project-id", required=True, help="Project id from governance/project_registry.yaml")
    parser.add_argument(
        "--output",
        help="Write stub YAML to this path (only repo-ops-dashboard root or governance/stubs/)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print YAML to stdout (default when --output omitted)")
    return parser.parse_args()


def allowed_output_path(root: Path, output: Path) -> bool:
    output = output.resolve()
    root = root.resolve()
    if output == root / "repo_context_index.yaml":
        return True
    stubs = root / "governance" / "stubs"
    try:
        output.relative_to(stubs)
        return True
    except ValueError:
        return False


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    registry_path = root / "governance" / "project_registry.yaml"
    try:
        project = find_project(load_registry(registry_path), args.project_id)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    repo_path = Path(str(project.get("path", "")))
    summary = first_line_summary(repo_path / ALLOWLIST_README) if repo_path.is_dir() else "Repository path unavailable."
    stub = build_repo_context_index_stub(
        project_id=str(project.get("project_id")),
        repo_name=str(project.get("repo_name")),
        domain=str(project.get("domain", "unknown")),
        current_stage=str(project.get("lifecycle", "active")),
        summary=summary,
        roadmap_summary="See project roadmap or docs/index.md when available.",
        next_actions=["Add repo_context_index.yaml to repository root if missing."],
    )
    errors = validate_repo_context_index(stub, args.project_id)
    if errors:
        print(f"[invalid] {errors[0]}", file=sys.stderr)
        return 1

    body = yaml.safe_dump(stub, allow_unicode=True, sort_keys=False, default_flow_style=False)
    header = "# repo_context_index stub — review before copying to managed repo root.\n"

    if args.output:
        output_path = Path(args.output)
        if args.project_id != THIS_REPO_ID and not str(output_path).startswith(str(root / "governance" / "stubs")):
            print("[error] managed repos are read-only; write only to governance/stubs/ or this repo root", file=sys.stderr)
            return 2
        if not allowed_output_path(root, output_path):
            print("[error] output path not allowed", file=sys.stderr)
            return 2
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(header + body, encoding="utf-8")
        print(f"[ok] wrote stub: {output_path}")
        return 0

    print(header + body, end="")
    if args.dry_run:
        print("[dry-run] stub printed to stdout", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
