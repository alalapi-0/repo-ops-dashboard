#!/usr/bin/env python3
"""Personal Agent OS long-term integration snapshot — portfolio + budget + digest (mock modules, dry-run)."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

DEFAULT_POLICY = "config/personal_os_integration_policy.yaml"
DEFAULT_SNAPSHOT = "governance/digests/daily/personal_os_integration.snapshot.yaml"
DEFAULT_REPORT = "reports/personal_os_integration.md"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else {}


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def count_projects(portfolio: dict[str, Any]) -> int:
    projects = portfolio.get("projects", [])
    return len(projects) if isinstance(projects, list) else 0


def budget_summary(budget: dict[str, Any]) -> dict[str, Any]:
    entries = budget.get("entries", [])
    if not isinstance(entries, list):
        entries = []
    total = sum(float(e.get("amount_usd", 0) or 0) for e in entries if isinstance(e, dict))
    return {"entry_count": len(entries), "total_usd": round(total, 2)}


def digest_headline(digest_text: str) -> str:
    for line in digest_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- next：") or stripped.startswith("- next:"):
            return stripped
    return ""


def build_mock_modules(cfg: dict[str, Any]) -> dict[str, Any]:
    mocks = cfg.get("mock_modules", {})
    result: dict[str, Any] = {}
    for name, meta in mocks.items():
        if isinstance(meta, dict):
            result[name] = {"status": "mock", "source": meta.get("source", "mock"), "note": meta.get("note", "")}
    return result


def build_snapshot(
    *,
    round_state: dict[str, Any],
    portfolio: dict[str, Any],
    budget: dict[str, Any],
    digest_headline: str,
    mock_modules: dict[str, Any],
    architecture_complete: bool,
) -> dict[str, Any]:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "schema_version": "0.1.0",
        "role": "personal_os_integration",
        "generated_at": ts,
        "architecture_40_rounds_complete": architecture_complete,
        "current_round": round_state.get("current_round", ""),
        "next_round": round_state.get("next_round", ""),
        "portfolio": {
            "project_count": count_projects(portfolio),
            "snapshot_at": portfolio.get("snapshot_at", ""),
        },
        "budget": budget_summary(budget),
        "weekly_digest_headline": digest_headline,
        "mock_modules": mock_modules,
        "external_api_called": False,
        "hitl_required": True,
    }


def render_report(snapshot: dict[str, Any], *, dry_run: bool) -> str:
    mode = "dry-run" if dry_run else "write"
    lines = [
        "# Personal Agent OS Integration Snapshot",
        "",
        f"- generated_at: {snapshot.get('generated_at', '')}",
        f"- mode: {mode}",
        f"- architecture_40_rounds_complete: {snapshot.get('architecture_40_rounds_complete')}",
        f"- current_round: {snapshot.get('current_round', '')}",
        f"- next_round: {snapshot.get('next_round', '')}",
        "",
        "## Portfolio",
        "",
        f"- project_count: {snapshot.get('portfolio', {}).get('project_count', 0)}",
        "",
        "## Budget (tracked)",
        "",
        f"- entries: {snapshot.get('budget', {}).get('entry_count', 0)}",
        f"- total_usd: {snapshot.get('budget', {}).get('total_usd', 0)}",
        "",
        "## Weekly Digest",
        "",
        f"- headline: {snapshot.get('weekly_digest_headline', '—')}",
        "",
        "## Mock Modules (HITL for live data)",
        "",
    ]
    for name, meta in (snapshot.get("mock_modules") or {}).items():
        lines.append(f"- **{name}**: {meta.get('note', '')}")
    lines.extend(
        [
            "",
            "## 40-Round Architecture",
            "",
            "Architecture rounds 02–40 mapped to repo rounds 25–63 are complete.",
            "Maintenance mode: incremental hardening, HumanOwner-driven priorities.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Personal Agent OS integration snapshot (dry-run default)")
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--output-snapshot", default=DEFAULT_SNAPSHOT)
    parser.add_argument("--output-report", default=DEFAULT_REPORT)
    parser.add_argument("--write", action="store_true", help="Write snapshot and report (default dry-run)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    policy = load_yaml(root / args.policy)
    integration = policy.get("integration", {})

    round_state = load_yaml(root / str(integration.get("round_state", "round_state/current_round.yaml")))
    portfolio = load_yaml(root / str(integration.get("portfolio", "governance/portfolio_state.yaml")))
    budget = load_yaml(root / str(integration.get("budget", "governance/budget_cost_tracking.yaml")))
    digest_text = load_text(root / str(integration.get("weekly_digest", "governance/digests/weekly/weekly_digest.md")))
    mock_modules = build_mock_modules(policy)

    next_round = str(round_state.get("next_round", ""))
    architecture_complete = next_round in {"", "maintenance_mode", "round_63_personal_agent_os_long_term_integration"}

    snapshot = build_snapshot(
        round_state=round_state,
        portfolio=portfolio,
        budget=budget,
        digest_headline=digest_headline(digest_text),
        mock_modules=mock_modules,
        architecture_complete=architecture_complete,
    )
    report = render_report(snapshot, dry_run=not args.write)

    if args.write:
        snap_path = root / args.output_snapshot
        report_path = root / args.output_report
        snap_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        snap_path.write_text(
            yaml.safe_dump(snapshot, allow_unicode=True, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )
        report_path.write_text(report, encoding="utf-8")
        print(f"[integration] snapshot -> {snap_path}")
        print(f"[integration] report -> {report_path}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
