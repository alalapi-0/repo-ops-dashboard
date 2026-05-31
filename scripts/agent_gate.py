#!/usr/bin/env python3
"""Deterministic safety gate for repo-ops-dashboard."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc


PASS = "PASS"
WARNING = "WARNING"
BLOCKED = "BLOCKED"
SEVERITY_ORDER = {PASS: 0, WARNING: 1, BLOCKED: 2}
EXIT_CODES = {PASS: 0, WARNING: 1, BLOCKED: 2}


@dataclass
class Finding:
    check: str
    severity: str
    message: str


class GateState:
    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def add(self, check: str, severity: str, message: str) -> None:
        self.findings.append(Finding(check=check, severity=severity, message=message))

    @property
    def verdict(self) -> str:
        if not self.findings:
            return PASS
        return max(self.findings, key=lambda x: SEVERITY_ORDER[x.severity]).severity


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def run_git_lines(command: list[str], cwd: Path) -> list[str]:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            check=False,
            text=True,
            capture_output=True,
        )
    except OSError:
        return []
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def check_denylist(state: GateState, root: Path) -> None:
    cfg = load_yaml(root / "config" / "managed_files.yaml")
    denylist = cfg.get("denylist", [])
    allowlist = cfg.get("allowlist", [])
    if not denylist:
        state.add("denylist", BLOCKED, "config/managed_files.yaml denylist is empty")
        return
    overlap = [item for item in allowlist if any(token in item.lower() for token in ["env", "token", "secret"])]
    if overlap:
        state.add("denylist", WARNING, f"suspicious allowlist entries: {overlap}")
    else:
        state.add("denylist", PASS, "denylist configured")


def check_local_required_files(state: GateState, root: Path) -> None:
    required = [
        "README.md",
        "AGENTS.md",
        "repo_protocol_standard.yaml",
        "round_state/current_round.yaml",
    ]
    missing = [item for item in required if not (root / item).exists()]
    if missing:
        state.add("required_files", BLOCKED, f"missing required files: {missing}")
    else:
        state.add("required_files", PASS, "required governance files exist")


def check_env_git_risk(state: GateState, root: Path) -> None:
    tracked = run_git_lines(["git", "ls-files", ".env", ".env.*"], root)
    if tracked:
        state.add("env_tracked", BLOCKED, f".env tracked by git: {tracked}")
    else:
        state.add("env_tracked", PASS, ".env is not tracked")


def check_secret_patterns(state: GateState, root: Path) -> None:
    candidates = run_git_lines(["git", "ls-files"], root)
    patterns = [
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"(?i)api[_-]?key\\s*[:=]\\s*['\\\"][A-Za-z0-9_\\-]{16,}"),
        re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH|PRIVATE) KEY-----"),
    ]
    hits: list[str] = []
    for rel in candidates:
        path = root / rel
        if not path.is_file() or path.stat().st_size > 1024 * 512:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for idx, line in enumerate(text.splitlines(), start=1):
            if any(pat.search(line) for pat in patterns):
                hits.append(f"{rel}:{idx}")
                if len(hits) >= 5:
                    break
        if len(hits) >= 5:
            break
    if hits:
        state.add("secret_pattern", BLOCKED, f"possible secret patterns at {hits}")
    else:
        state.add("secret_pattern", PASS, "no obvious secret patterns in tracked files")


def check_script_defaults(state: GateState, root: Path) -> None:
    scripts = sorted((root / "scripts").glob("*.py"))
    missing = []
    for script in scripts:
        text = script.read_text(encoding="utf-8")
        if script.name == "scan_repos.py" and "--dry-run" not in text:
            missing.append(script.name)
    if missing:
        state.add("dry_run_defaults", WARNING, f"dry-run markers missing in: {missing}")
    else:
        state.add("dry_run_defaults", PASS, "dry-run defaults checked")


def check_no_target_repo_modification_logic(state: GateState, root: Path) -> None:
    risky_tokens = ["git commit", "git push", "shutil.rmtree", "os.remove(", "Path.unlink("]
    script_dir = root / "scripts"
    findings: list[str] = []
    for path in sorted(script_dir.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        for token in risky_tokens:
            if token in text:
                findings.append(f"{path.name}:{token}")
    if findings:
        state.add("target_repo_modification", WARNING, f"review risky tokens: {findings}")
    else:
        state.add("target_repo_modification", PASS, "no obvious target-repo write logic")


def check_integration_is_docs_only(state: GateState, root: Path) -> None:
    script_dir = root / "scripts"
    risky_imports = ["feishu", "lark_oapi", "telegram", "openclaw_sdk"]
    hits = []
    for path in sorted(script_dir.glob("*.py")):
        text = path.read_text(encoding="utf-8").lower()
        for key in risky_imports:
            if key in text:
                hits.append(f"{path.name}:{key}")
    if hits:
        state.add("integration_docs_only", WARNING, f"integration keyword found: {hits}")
    else:
        state.add("integration_docs_only", PASS, "integrations remain docs-only")


def render_report(state: GateState, root: Path) -> Path:
    report_path = root / "reports" / "agent_gate_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Gate Report",
        "",
        f"- generated_at: {datetime.now(timezone.utc).isoformat()}",
        f"- verdict: {state.verdict}",
        "",
        "## Findings",
    ]
    for item in state.findings:
        lines.append(f"- [{item.severity}] `{item.check}`: {item.message}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic gate checks")
    parser.add_argument("--root", default=".", help="Repository root path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    state = GateState()

    check_denylist(state, root)
    check_local_required_files(state, root)
    check_env_git_risk(state, root)
    check_secret_patterns(state, root)
    check_script_defaults(state, root)
    check_no_target_repo_modification_logic(state, root)
    check_integration_is_docs_only(state, root)
    report = render_report(state, root)

    print(f"[gate] verdict={state.verdict} report={report}")
    for item in state.findings:
        print(f"[{item.severity}] {item.check}: {item.message}")
    return EXIT_CODES[state.verdict]


if __name__ == "__main__":
    raise SystemExit(main())
