#!/usr/bin/env python3
"""Portfolio governance hardening audit — security, docs consistency (dry-run default)."""

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

DEFAULT_POLICY = "config/governance_hardening_policy.yaml"
DEFAULT_REPORT = "reports/governance_hardening_audit.md"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else {}


def check_denylist(root: Path, cfg_path: str) -> tuple[str, str]:
    cfg = load_yaml(root / cfg_path)
    denylist = cfg.get("denylist", [])
    if not denylist:
        return "BLOCKED", "denylist is empty"
    return "PASS", f"denylist has {len(denylist)} entries"


def check_required_docs(root: Path, docs: list[str]) -> tuple[str, str]:
    missing = [doc for doc in docs if not (root / doc).exists()]
    if missing:
        return "WARNING", f"missing round docs: {missing}"
    return "PASS", f"all {len(docs)} required round docs present"


def check_protocol_agents_alignment(root: Path, protocol_path: str, agents_path: str) -> tuple[str, str]:
    protocol = root / protocol_path
    agents = root / agents_path
    if not protocol.exists() or not agents.exists():
        return "BLOCKED", "protocol or AGENTS.md missing"
    p_text = protocol.read_text(encoding="utf-8")
    a_text = agents.read_text(encoding="utf-8")
    keywords = ["HumanOwner", "proof_of_work", "review_queue", "task_spec"]
    gaps = [kw for kw in keywords if kw in p_text and kw not in a_text]
    if gaps:
        return "WARNING", f"AGENTS.md missing protocol keywords: {gaps}"
    return "PASS", "AGENTS.md aligns with protocol keywords"


def scan_script_security(
    root: Path,
    *,
    forbidden: list[str],
    allowed_sources: list[str],
) -> tuple[str, str]:
    scripts_dir = root / "scripts"
    if not scripts_dir.is_dir():
        return "BLOCKED", "scripts/ directory missing"
    violations: list[str] = []
    for path in sorted(scripts_dir.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        if rel in allowed_sources:
            continue
        for pattern in forbidden:
            if pattern in text:
                violations.append(f"{rel}: {pattern}")
    if violations:
        return "WARNING", f"suspicious patterns: {violations[:5]}"
    return "PASS", f"scanned {len(list(scripts_dir.glob('*.py')))} scripts, no forbidden .env reads"


def check_error_handling(root: Path) -> tuple[str, str]:
    key_scripts = [
        "scripts/run_handoff_trial.py",
        "scripts/openclaw_daily_briefing_skill.py",
        "scripts/agent_gate.py",
    ]
    missing_guard: list[str] = []
    for rel in key_scripts:
        path = root / rel
        if not path.exists():
            missing_guard.append(f"{rel} missing")
            continue
        text = path.read_text(encoding="utf-8")
        if "SystemExit" not in text and "raise " not in text and "except " not in text:
            missing_guard.append(f"{rel} lacks error handling")
    if missing_guard:
        return "WARNING", "; ".join(missing_guard)
    return "PASS", "key scripts have error handling guards"


def render_report(
    *,
    findings: list[tuple[str, str, str]],
    dry_run: bool,
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Governance Hardening Audit",
        "",
        f"- generated_at: {ts}",
        f"- mode: {'dry-run' if dry_run else 'write'}",
        "",
        "## Findings",
        "",
        "| Check | Severity | Message |",
        "|-------|----------|---------|",
    ]
    for check, severity, message in findings:
        lines.append(f"| {check} | {severity} | {message} |")
    blocked = [s for _, s, _ in findings if s == "BLOCKED"]
    warnings = [s for _, s, _ in findings if s == "WARNING"]
    verdict = "BLOCKED" if blocked else ("WARNING" if warnings else "PASS")
    lines.extend(["", f"## Verdict: {verdict}", ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit portfolio governance hardening")
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--output-report", default=DEFAULT_REPORT)
    parser.add_argument("--write", action="store_true", help="Write report (default dry-run prints only)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    policy = load_yaml(root / args.policy)
    audit_cfg = policy.get("audit", {})
    security_cfg = policy.get("security", {})
    dry_run = not args.write

    findings: list[tuple[str, str, str]] = []

    sev, msg = check_denylist(root, str(audit_cfg.get("denylist_config", "config/managed_files.yaml")))
    findings.append(("denylist", sev, msg))

    round_docs = [str(d) for d in audit_cfg.get("required_round_docs", [])]
    sev, msg = check_required_docs(root, round_docs)
    findings.append(("round_docs", sev, msg))

    sev, msg = check_protocol_agents_alignment(
        root,
        str(audit_cfg.get("protocol_doc", "repo_protocol_standard.yaml")),
        str(audit_cfg.get("agents_doc", "AGENTS.md")),
    )
    findings.append(("protocol_agents", sev, msg))

    forbidden = [str(p) for p in security_cfg.get("forbidden_script_patterns", [])]
    allowed = [str(p) for p in security_cfg.get("allowed_env_sources", [])]
    sev, msg = scan_script_security(root, forbidden=forbidden, allowed_sources=allowed)
    findings.append(("script_security", sev, msg))

    sev, msg = check_error_handling(root)
    findings.append(("error_handling", sev, msg))

    report = render_report(findings=findings, dry_run=dry_run)
    report_path = root / args.output_report
    if args.write:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"[audit] wrote {report_path}")
    else:
        print(report)

    blocked = any(s == "BLOCKED" for _, s, _ in findings)
    return 2 if blocked else (1 if any(s == "WARNING" for _, s, _ in findings) else 0)


if __name__ == "__main__":
    raise SystemExit(main())
