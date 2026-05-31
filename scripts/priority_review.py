#!/usr/bin/env python3
"""Generate suggested priority review from repo status and factor config."""

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


def score_repo(repo: dict[str, Any], factors: dict[str, Any]) -> tuple[int, str, list[str]]:
    type_scores = dict(factors.get("type_scores", {}))
    repo_type = str(repo.get("type", "unknown"))
    type_score = int(type_scores.get(repo_type, type_scores.get("unknown", 0)))

    health = int(repo.get("health_score", 0))
    health_weight = float(factors.get("health_weight", 0.35))
    demo_value = int(health * health_weight)

    total = type_score + demo_value
    reasons: list[str] = [
        f"type={repo_type} (+{type_score})",
        f"health={health} → demo (+{demo_value})",
    ]

    if repo.get("blockers"):
        penalty = int(factors.get("blocker_penalty", 25))
        total -= penalty
        reasons.append(f"blockers (-{penalty})")
    if repo.get("archive_candidate"):
        penalty = int(factors.get("archive_penalty", 100))
        total -= penalty
        reasons.append(f"archive_candidate (-{penalty})")
    elif repo.get("freeze_candidate"):
        penalty = int(factors.get("freeze_penalty", 15))
        total -= penalty
        reasons.append(f"freeze_candidate (-{penalty})")

    thresholds = dict(factors.get("thresholds", {}))
    high_cut = int(thresholds.get("high", 55))
    medium_cut = int(thresholds.get("medium", 30))
    if total >= high_cut:
        suggested = "high"
    elif total >= medium_cut:
        suggested = "medium"
    else:
        suggested = "low"

    return total, suggested, reasons


def human_hint_map(repos_config: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in repos_config.get("repos", []):
        name = str(row.get("name", ""))
        hint = str(row.get("priority_hint", "")).lower()
        if name and hint in {"high", "medium", "low"}:
            out[name] = hint
    return out


def build_board(
    status: dict[str, Any],
    factors: dict[str, Any],
    hints: dict[str, str],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    high: list[str] = []
    blocked: list[str] = []
    freeze_candidates: list[str] = []
    archive_candidates: list[str] = []

    for repo in status.get("repos", []):
        name = str(repo.get("name", ""))
        score, suggested, reasons = score_repo(repo, factors)
        human = hints.get(name, "")
        final = human or suggested
        source = "human_override" if human else "suggested"

        if final == "high":
            high.append(name)
        if repo.get("blockers"):
            blocked.append(name)
        if repo.get("freeze_candidate"):
            freeze_candidates.append(name)
        if repo.get("archive_candidate"):
            archive_candidates.append(name)

        entries.append(
            {
                "name": name,
                "score": score,
                "suggested_priority": suggested,
                "final_priority": final,
                "priority_source": source,
                "reasons": reasons,
                "human_hint": human or None,
                "current_analyzer_priority": repo.get("priority"),
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "high_priority": high,
        "blocked": blocked,
        "freeze_candidates": freeze_candidates,
        "archive_candidates": archive_candidates,
        "repos": entries,
    }


def render_report(board: dict[str, Any], factors: dict[str, Any]) -> str:
    labels = dict(factors.get("factor_labels", {}))
    lines = [
        "# Priority Review",
        "",
        f"- generated_at: {board['generated_at']}",
        "- 说明：以下为**建议**优先级；Human 在 `config/repos.yaml` 的 `priority_hint` 中覆盖后，`final_priority` 以人工为准。",
        "",
        "## 因素说明",
    ]
    for key, label in labels.items():
        lines.append(f"- **{key}**: {label}")

    lines.extend(["", "## 仓库建议", ""])
    for row in board.get("repos", []):
        src = "人工覆盖" if row["priority_source"] == "human_override" else "算法建议"
        lines.append(f"### {row['name']}")
        lines.append(f"- 得分: {row['score']}")
        lines.append(f"- 建议: {row['suggested_priority']} → 最终: **{row['final_priority']}** ({src})")
        lines.append(f"- 理由: {'; '.join(row['reasons'])}")
        if row.get("human_hint"):
            lines.append(f"- Human hint: {row['human_hint']}")
        lines.append("")

    lines.extend(
        [
            "## 汇总",
            "",
            f"- 高优先级: {', '.join(board.get('high_priority', [])) or '无'}",
            f"- 卡点: {', '.join(board.get('blocked', [])) or '无'}",
            f"- 冻结候选: {', '.join(board.get('freeze_candidates', [])) or '无'}",
            f"- 归档候选: {', '.join(board.get('archive_candidates', [])) or '无'}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate priority review report")
    parser.add_argument("--input", default="data/repo_status.json", help="Repo status JSON")
    parser.add_argument("--repos-config", default="config/repos.yaml", help="Registry with priority_hint")
    parser.add_argument("--factors", default="config/priority_factors.yaml", help="Factor weights")
    parser.add_argument("--output-board", default="data/priority_board.json", help="Local board JSON")
    parser.add_argument("--output-report", default="reports/priority_review.md", help="Markdown report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status_path = Path(args.input)
    if not status_path.exists():
        raise SystemExit(f"Status not found: {status_path}")

    status = load_json(status_path)
    factors = load_yaml(Path(args.factors))
    repos_path = Path(args.repos_config)
    hints = human_hint_map(load_yaml(repos_path)) if repos_path.exists() else {}

    board = build_board(status, factors, hints)

    board_path = Path(args.output_board)
    board_path.parent.mkdir(parents=True, exist_ok=True)
    board_path.write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8")

    report_path = Path(args.output_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(board, factors), encoding="utf-8")

    print(f"[ok] priority board -> {board_path}")
    print(f"[ok] priority review -> {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
