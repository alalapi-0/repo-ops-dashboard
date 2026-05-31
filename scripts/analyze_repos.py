#!/usr/bin/env python3
"""Rule-based repository status analyzer."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def compute_health(repo: dict[str, Any], weights: dict[str, int]) -> int:
    score = 0
    files = set(repo.get("read_files", []))
    warnings = repo.get("warnings", [])
    status = str(repo.get("status", "unknown"))

    if any(item.startswith("README") for item in files):
        score += int(weights.get("readme_exists", 0))
    if "AGENTS.md" in files:
        score += int(weights.get("agents_exists", 0))
    if "repo_protocol_standard.yaml" in files:
        score += int(weights.get("protocol_exists", 0))
    if "CHANGELOG.md" in files:
        score += int(weights.get("changelog_exists", 0))
    if any(item.startswith("round_state/") for item in files):
        score += int(weights.get("round_state_exists", 0))
    if "docs/index.md" in files:
        score += int(weights.get("docs_index_exists", 0))
    if status in {"active", "bootstrap"}:
        score += int(weights.get("recent_update", 0))
    if not any("next action missing" in str(w).lower() for w in warnings):
        score += int(weights.get("has_next_action", 0))
    if not warnings:
        score += int(weights.get("no_blocker", 0))

    return min(max(score, 0), 100)


def pick_priority(repo: dict[str, Any], health_score: int) -> str:
    status = str(repo.get("status", "unknown"))
    repo_type = str(repo.get("type", "unknown"))

    if status == "missing":
        return "low"
    if status in {"active", "bootstrap"} and repo_type in {"meta_ops", "novel_agent", "ai_manga"}:
        return "high"
    if health_score >= 70:
        return "medium"
    return "low"


def infer_stage(repo: dict[str, Any]) -> str:
    status = str(repo.get("status", "unknown"))
    if status == "missing":
        return "missing"
    if status == "bootstrap":
        return "round_00_bootstrap"
    if status == "active":
        return "execution"
    return "unknown"


def recommend_agent(priority: str, blockers: list[str], repo_type: str) -> str:
    if blockers and "missing" in " ".join(blockers).lower():
        return "Human"
    if repo_type == "meta_ops":
        return "Cursor"
    if priority == "high":
        return "Codex"
    return "Cursor"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze repository snapshots")
    parser.add_argument("--input", default="data/repo_snapshots.json", help="Input snapshots json")
    parser.add_argument("--output", default="data/repo_status.json", help="Output status json")
    parser.add_argument("--rules", default="config/scoring_rules.yaml", help="Scoring rules yaml")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    rules_path = Path(args.rules)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")
    if not rules_path.exists():
        raise SystemExit(f"Rules not found: {rules_path}")

    snapshots = load_json(input_path)
    rules = load_yaml(rules_path)
    weights = dict(rules.get("health_score", {}))

    repos_out: list[dict[str, Any]] = []
    for repo in snapshots.get("repos", []):
        health = compute_health(repo, weights)
        priority = pick_priority(repo, health)
        blockers = list(repo.get("warnings", []))
        next_actions = []
        if repo.get("status") == "missing":
            next_actions.append("确认仓库路径是否有效")
        else:
            if blockers:
                next_actions.append("补齐缺失治理文件并修复 warning")
            else:
                next_actions.append("继续执行下一轮计划")

        freeze_candidate = health < 40 or repo.get("status") == "missing"
        archive_candidate = repo.get("status") == "missing" and repo.get("type") == "demo"
        recommended_agent = recommend_agent(priority, blockers, str(repo.get("type", "unknown")))

        repos_out.append(
            {
                "name": repo.get("name"),
                "path": repo.get("path"),
                "type": repo.get("type"),
                "status": repo.get("status"),
                "current_stage": infer_stage(repo),
                "health_score": health,
                "priority": priority,
                "blockers": blockers,
                "next_actions": next_actions,
                "recommended_agent": recommended_agent,
                "freeze_candidate": freeze_candidate,
                "archive_candidate": archive_candidate,
            }
        )

    result = {"generated_at": datetime.now(timezone.utc).isoformat(), "repos": repos_out}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    high_count = sum(1 for repo in repos_out if repo["priority"] == "high")
    blocked_count = sum(1 for repo in repos_out if repo["blockers"])
    print(f"[ok] repos={len(repos_out)} high={high_count} blocked={blocked_count} -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
