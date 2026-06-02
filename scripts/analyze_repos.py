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

from priority_scoring import compute_priority_score


ANALYZER_VERSION = "v2"
ROUND_STATE_REL = "round_state/current_round.yaml"
MAX_ROUND_STATE_BYTES = 64 * 1024


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


CRITICAL_MISSING = {"AGENTS.md", "repo_protocol_standard.yaml", "README.md"}


def repo_issue_messages(repo: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    for key in ("missing", "skipped", "warnings"):
        for item in repo.get(key, []):
            text = str(item)
            if text not in messages:
                messages.append(text)
    return messages


def derive_blockers(repo: dict[str, Any]) -> list[str]:
    status = str(repo.get("status", "unknown"))
    if status in {"missing", "empty"}:
        if status == "empty":
            return ["repository directory empty"]
        return list(repo.get("missing", [])) or ["repository path missing"]

    blockers: list[str] = []
    for item in repo.get("missing", []):
        name = str(item)
        if name in CRITICAL_MISSING:
            blockers.append(f"{name} missing")
    return blockers


def derive_lifecycle(
    repo: dict[str, Any],
    *,
    registry_lifecycle: str = "",
    registry_matched: bool = True,
    health_score: int = 0,
    policy: dict[str, Any] | None = None,
) -> str:
    if policy:
        return derive_lifecycle_v1(
            repo,
            registry_lifecycle=registry_lifecycle,
            registry_matched=registry_matched,
            health_score=health_score,
            policy=policy,
        )
    if repo.get("archive_candidate"):
        return "archived"
    status = str(repo.get("status", "unknown"))
    if status in {"missing", "empty"}:
        return status
    if repo.get("freeze_candidate"):
        return "freeze_candidate"
    if status == "bootstrap":
        return "bootstrap"
    if status == "active":
        return "active"
    return status


def derive_lifecycle_v1(
    repo: dict[str, Any],
    *,
    registry_lifecycle: str = "",
    registry_matched: bool = True,
    health_score: int = 0,
    policy: dict[str, Any],
) -> str:
    rules = dict(policy.get("rules", {}))
    reg = str(registry_lifecycle or "").lower()

    if reg == "abandoned":
        return str(rules.get("registry_abandoned", "abandoned"))
    if reg == "idea":
        return str(rules.get("registry_idea", "idea"))
    if repo.get("archive_candidate"):
        return str(rules.get("archive_candidate", "archived"))
    status = str(repo.get("status", "unknown"))
    if status == "missing":
        return str(rules.get("status_missing", "archived"))
    if status == "empty":
        return str(rules.get("status_empty", "archived"))
    if repo.get("blockers"):
        return str(rules.get("has_blockers", "blocked"))
    if repo.get("freeze_candidate"):
        return str(rules.get("freeze_candidate", "frozen"))
    if status == "bootstrap":
        return str(rules.get("status_bootstrap", "bootstrap"))
    maint_cfg = rules.get("low_health_maintenance", {})
    threshold = 40
    if isinstance(maint_cfg, dict):
        threshold = int(maint_cfg.get("threshold", 40))
    if status == "active" and health_score < threshold:
        return str(maint_cfg.get("status_active", "maintenance") if isinstance(maint_cfg, dict) else "maintenance")
    if not registry_matched:
        return str(rules.get("unmatched_registry", "idea"))
    if status == "active":
        return str(rules.get("default_active", "active"))
    allowed = set(policy.get("states", []))
    if allowed and status in allowed:
        return status
    return str(rules.get("default_active", "active"))


def build_registry_index(registry_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_path: dict[str, dict[str, Any]] = {}
    by_name: dict[str, dict[str, Any]] = {}
    for project in registry_data.get("projects", []):
        if not isinstance(project, dict):
            continue
        path = str(project.get("path", "")).rstrip("/")
        name = str(project.get("repo_name", ""))
        if path:
            by_path[path] = project
        if name:
            by_name[name] = project
    return {"by_path": by_path, "by_name": by_name}


def match_registry_project(repo: dict[str, Any], index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    path = str(repo.get("path", "")).rstrip("/")
    name = str(repo.get("name", ""))
    return index.get("by_path", {}).get(path) or index.get("by_name", {}).get(name) or {}


def read_round_state_summary(repo_path: Path, read_files: list[str]) -> dict[str, str]:
    if ROUND_STATE_REL not in read_files:
        return {}
    target = repo_path / ROUND_STATE_REL
    if not target.is_file():
        return {}
    try:
        size = target.stat().st_size
    except OSError:
        return {}
    if size > MAX_ROUND_STATE_BYTES:
        return {"status": "too_large"}
    try:
        data = load_yaml(target)
    except (OSError, yaml.YAMLError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        "current_round": str(data.get("current_round", "")),
        "status": str(data.get("status", "")),
        "next_round": str(data.get("next_round", "")),
    }


def score_governance_dimension(repo: dict[str, Any]) -> int:
    core = repo.get("core_governance")
    if isinstance(core, dict) and "required_coverage_pct" in core:
        return int(core.get("required_coverage_pct", 0))
    files = set(repo.get("read_files", []))
    checks = [
        any(item.startswith("README") for item in files),
        "AGENTS.md" in files,
        "repo_protocol_standard.yaml" in files,
    ]
    return int(round(sum(checks) * 100 / len(checks)))


def score_registry_dimension(repo: dict[str, Any], registry_project: dict[str, Any]) -> int:
    if not registry_project:
        return 0
    score = 70
    registry_lifecycle = str(registry_project.get("lifecycle", ""))
    snapshot_status = str(repo.get("status", ""))
    if registry_lifecycle and snapshot_status and registry_lifecycle != snapshot_status:
        score -= 20
    registry_domain = str(registry_project.get("domain", ""))
    repo_type = str(repo.get("type", ""))
    if registry_domain and repo_type and registry_domain.replace("_", "-") not in repo_type.replace("_", "-"):
        if registry_domain != repo_type:
            score -= 10
    return max(score, 0)


def score_round_progress_dimension(round_state: dict[str, str]) -> int:
    if not round_state:
        return 0
    if round_state.get("status") == "too_large":
        return 20
    status = str(round_state.get("status", "")).lower()
    if status == "completed":
        return 100
    if status in {"in_progress", "active", "running"}:
        return 60
    if status:
        return 40
    if round_state.get("current_round"):
        return 50
    return 0


def compute_health_dimensions(
    repo: dict[str, Any],
    registry_project: dict[str, Any],
    round_state: dict[str, str],
    dimension_weights: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    scores = {
        "governance_files": score_governance_dimension(repo),
        "registry_alignment": score_registry_dimension(repo, registry_project),
        "round_progress": score_round_progress_dimension(round_state),
    }
    total_weight = 0
    weighted_total = 0
    breakdown: dict[str, Any] = {}
    for name, raw_score in scores.items():
        entry = dimension_weights.get(name, {})
        weight = int(entry.get("weight", 0)) if isinstance(entry, dict) else 0
        contribution = int(round(raw_score * weight / 100)) if weight else 0
        breakdown[name] = {"score": raw_score, "weight": weight, "contribution": contribution}
        total_weight += weight
        weighted_total += contribution
    composite = int(round(weighted_total * 100 / total_weight)) if total_weight else 0
    return {"composite_score": composite, "breakdown": breakdown}


def compute_health(repo: dict[str, Any], weights: dict[str, int]) -> int:
    score = 0
    files = set(repo.get("read_files", []))
    warning_count = len(repo.get("warnings", []))
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
    if not any("next action missing" in str(w).lower() for w in repo.get("warnings", [])):
        score += int(weights.get("has_next_action", 0))
    blockers = derive_blockers(repo)
    if not blockers and not repo.get("warnings"):
        score += int(weights.get("no_blocker", 0))

    score -= min(warning_count * 2, 20)
    return min(max(score, 0), 100)


def pick_priority(repo: dict[str, Any], health_score: int) -> str:
    status = str(repo.get("status", "unknown"))
    repo_type = str(repo.get("type", "unknown"))

    if status in {"missing", "empty"}:
        return "low"
    hint = str(repo.get("priority_hint", "")).lower()
    if hint in {"high", "medium", "low"}:
        return hint
    if status in {"active", "bootstrap"} and repo_type in {"meta_ops", "novel_agent", "ai_manga", "ai_anime", "content_scheduler"}:
        return "high"
    if health_score >= 70:
        return "medium"
    return "low"


def infer_stage(repo: dict[str, Any]) -> str:
    status = str(repo.get("status", "unknown"))
    if status in {"missing", "empty"}:
        return status
    if status == "bootstrap":
        return "round_00_bootstrap"
    if status == "active":
        return "execution"
    return "unknown"


def recommend_agent(priority: str, blockers: list[str], repo_type: str, archive_candidate: bool) -> str:
    if archive_candidate:
        return "Human"
    if blockers and any(
        token in " ".join(blockers).lower() for token in ("missing", "empty", "path")
    ):
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
    parser.add_argument("--registry", default="governance/project_registry.yaml", help="Project registry yaml")
    parser.add_argument("--analyzer-policy", default="config/analyzer_policy.yaml", help="Analyzer policy yaml")
    parser.add_argument(
        "--priority-scoring-policy",
        default="config/priority_scoring_policy.yaml",
        help="Priority scoring policy yaml",
    )
    parser.add_argument(
        "--lifecycle-policy",
        default="",
        help="Lifecycle policy yaml (optional until Round 37)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    rules_path = Path(args.rules)
    registry_path = Path(args.registry)
    policy_path = Path(args.analyzer_policy)
    scoring_policy_path = Path(args.priority_scoring_policy)
    lifecycle_policy_path = Path(args.lifecycle_policy) if args.lifecycle_policy else None
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")
    if not rules_path.exists():
        raise SystemExit(f"Rules not found: {rules_path}")
    if not registry_path.exists():
        raise SystemExit(f"Registry not found: {registry_path}")
    if not policy_path.exists():
        raise SystemExit(f"Analyzer policy not found: {policy_path}")
    if not scoring_policy_path.exists():
        raise SystemExit(f"Priority scoring policy not found: {scoring_policy_path}")
    lifecycle_policy: dict[str, Any] | None = None
    if lifecycle_policy_path:
        if not lifecycle_policy_path.exists():
            raise SystemExit(f"Lifecycle policy not found: {lifecycle_policy_path}")
        lifecycle_policy = load_yaml(lifecycle_policy_path)

    snapshots = load_json(input_path)
    rules = load_yaml(rules_path)
    registry_data = load_yaml(registry_path)
    policy_cfg = load_yaml(policy_path)
    scoring_policy = load_yaml(scoring_policy_path)
    weights = dict(rules.get("health_score", {}))
    dimension_weights = dict(policy_cfg.get("health_dimensions", {}))
    registry_index = build_registry_index(registry_data)

    repos_out: list[dict[str, Any]] = []
    snapshot_generated_at = str(snapshots.get("generated_at", ""))
    for repo in snapshots.get("repos", []):
        registry_project = match_registry_project(repo, registry_index)
        repo_path = Path(str(repo.get("path", "")))
        round_state = (
            read_round_state_summary(repo_path, list(repo.get("read_files", [])))
            if repo_path.exists() and repo_path.is_dir()
            else {}
        )
        health = compute_health(repo, weights)
        dimensions = compute_health_dimensions(repo, registry_project, round_state, dimension_weights)
        composite = int(dimensions.get("composite_score", 0))
        if registry_project:
            health = int(round((health + composite) / 2))
        priority = pick_priority(repo, health)
        blockers = derive_blockers(repo)
        warnings = list(repo.get("warnings", []))
        next_actions = []
        status = str(repo.get("status", "unknown"))
        if status == "missing":
            next_actions.append("确认仓库路径是否有效，或从登记中归档")
        elif status == "empty":
            next_actions.append("目录为空：归档登记或恢复项目内容")
        elif blockers:
            next_actions.append("补齐缺失治理文件（AGENTS.md / protocol / README）")
        elif warnings:
            next_actions.append("处理扫描 warning 并补齐可选治理文件")
        elif round_state.get("next_round"):
            next_actions.append(f"继续 {round_state.get('next_round')}")
        else:
            next_actions.append("继续执行下一轮计划")

        freeze_candidate = health < 40 or status in {"missing", "empty"}
        archive_candidate = status in {"missing", "empty"}
        recommended_agent = recommend_agent(
            priority,
            blockers,
            str(repo.get("type", "unknown")),
            archive_candidate,
        )

        scoring_input = {
            "name": repo.get("name"),
            "type": repo.get("type"),
            "status": repo.get("status"),
            "health_score": health,
            "registry_matched": bool(registry_project),
            "blockers": blockers,
            "warnings": warnings,
            "freeze_candidate": freeze_candidate,
            "archive_candidate": archive_candidate,
            "round_next": str(round_state.get("next_round", "")),
            "next_actions": next_actions,
        }
        score_fields = compute_priority_score(scoring_input, scoring_policy)

        lifecycle_status = derive_lifecycle(
            {
                **repo,
                "blockers": blockers,
                "freeze_candidate": freeze_candidate,
                "archive_candidate": archive_candidate,
            },
            registry_lifecycle=str(registry_project.get("lifecycle", "")),
            registry_matched=bool(registry_project),
            health_score=health,
            policy=lifecycle_policy,
        )

        row = {
            "name": repo.get("name"),
            "path": repo.get("path"),
            "type": repo.get("type"),
            "status": repo.get("status"),
            "project_id": str(registry_project.get("project_id", "")),
            "registry_matched": bool(registry_project),
            "registry_lifecycle": str(registry_project.get("lifecycle", "")),
            "governance_level": str(registry_project.get("governance_level", "")),
            "round_current": str(round_state.get("current_round", "")),
            "round_status": str(round_state.get("status", "")),
            "round_next": str(round_state.get("next_round", "")),
            "current_stage": infer_stage(repo),
            "health_score": health,
            "health_dimensions": dimensions,
            "priority": priority,
            "blockers": blockers,
            "warnings": warnings,
            "next_actions": next_actions,
            "recommended_agent": recommended_agent,
            "freeze_candidate": freeze_candidate,
            "archive_candidate": archive_candidate,
            "lifecycle_status": lifecycle_status,
            "last_checked": snapshot_generated_at,
            **score_fields,
        }
        repos_out.append(row)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analyzer_version": ANALYZER_VERSION,
        "analyzer_policy": policy_path.as_posix(),
        "priority_scoring_policy": scoring_policy_path.as_posix(),
        "registry": registry_path.as_posix(),
        "repos": repos_out,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    high_count = sum(1 for repo in repos_out if repo["priority"] == "high")
    blocked_count = sum(1 for repo in repos_out if repo["blockers"])
    print(f"[ok] repos={len(repos_out)} high={high_count} blocked={blocked_count} -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
