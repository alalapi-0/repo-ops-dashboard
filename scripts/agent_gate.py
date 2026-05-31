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

ROUND_FILES = [
    "round_00_bootstrap.md",
    "round_01_repo_registry.md",
    "round_02_readonly_scanner.md",
    "round_03_status_analyzer.md",
    "round_04_dashboard.md",
    "round_05_prompt_generator.md",
    "round_06_scheduler_and_reports.md",
    "round_07_openclaw_bridge.md",
    "round_08_feishu_notifications.md",
    "round_09_playwright_ui_check.md",
    "round_10_release_hardening.md",
    "round_11_repository_lifecycle_rules.md",
    "round_12_priority_review_system.md",
    "round_13_cross_repo_protocol_sync.md",
    "round_14_openclaw_daily_briefing.md",
    "round_15_long_term_personal_operating_system.md",
    "round_16_cursor_automation_feishu.md",
    "round_17_feishu_bitable_sync.md",
    "round_18_weekly_review_human_notes.md",
    "round_19_local_imports_optional.md",
    "round_20_env_template.md",
    "round_21_daily_brief_rename.md",
    "round_22_llm_openrouter.md",
    "round_23_feishu_hardening.md",
    "round_24_personal_os_hub.md",
]

ROUND_REQUIRED_SECTIONS = ["## 目标", "## 验收标准", "## 推荐执行 Agent"]


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
        re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}"),
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
        if path.name == "agent_gate.py":
            continue
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
    allowed_feishu_scripts = {"prepare_feishu_payload.py", "sync_feishu_bitable.py"}
    hits = []
    for path in sorted(script_dir.glob("*.py")):
        if path.name == "agent_gate.py":
            continue
        text = path.read_text(encoding="utf-8").lower()
        for key in risky_imports:
            if key in text:
                if key == "feishu" and path.name in allowed_feishu_scripts:
                    continue
                hits.append(f"{path.name}:{key}")
    if hits:
        state.add("integration_docs_only", WARNING, f"integration keyword found: {hits}")
    else:
        state.add("integration_docs_only", PASS, "integrations remain docs-only")


def check_round_docs_exist(state: GateState, root: Path) -> None:
    rounds_dir = root / "docs" / "rounds"
    missing = [name for name in ROUND_FILES if not (rounds_dir / name).exists()]
    if missing:
        state.add("round_docs", BLOCKED, f"missing round docs: {missing}")
    else:
        state.add("round_docs", PASS, f"round docs 00-{len(ROUND_FILES) - 1} exist")


def check_round_doc_sections(state: GateState, root: Path) -> None:
    rounds_dir = root / "docs" / "rounds"
    incomplete: list[str] = []
    for name in ROUND_FILES:
        path = rounds_dir / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        missing_sections = [sec for sec in ROUND_REQUIRED_SECTIONS if sec not in text]
        if missing_sections:
            incomplete.append(f"{name}: {missing_sections}")
    if incomplete:
        state.add("round_doc_sections", WARNING, f"incomplete sections: {incomplete[:5]}")
    else:
        state.add("round_doc_sections", PASS, "round docs contain required sections")


def check_ui_check_script(state: GateState, root: Path) -> None:
    path = root / "scripts" / "ui_check.py"
    if not path.exists():
        state.add("ui_check_script", WARNING, "scripts/ui_check.py missing")
    else:
        state.add("ui_check_script", PASS, "ui_check.py exists")


def check_audit_report(state: GateState, root: Path) -> None:
    path = root / "reports" / "round_01_independent_audit_report.md"
    if not path.exists():
        state.add("audit_report", WARNING, "reports/round_01_independent_audit_report.md missing")
    else:
        state.add("audit_report", PASS, "round 01 audit report exists")


def check_playwright_local_only(state: GateState, root: Path) -> None:
    path = root / "scripts" / "ui_check.py"
    if not path.exists():
        state.add("playwright_local", WARNING, "ui_check.py not present for review")
        return
    text = path.read_text(encoding="utf-8")
    external_hits = []
    for match in re.finditer(r"https?://[^\s'\"]+", text):
        url = match.group(0)
        if "playwright.dev" not in url and "example.com" not in url:
            external_hits.append(url)
    if "file://" in text or "as_uri()" in text:
        state.add("playwright_local", PASS, "ui_check uses local file:// access")
    elif external_hits:
        state.add("playwright_local", WARNING, f"ui_check may access external URLs: {external_hits}")
    else:
        state.add("playwright_local", WARNING, "ui_check local-only pattern not confirmed")


def check_scan_allowlist_compliance(state: GateState, root: Path) -> None:
    scan_path = root / "scripts" / "scan_repos.py"
    if not scan_path.exists():
        state.add("scan_allowlist", WARNING, "scan_repos.py missing")
        return
    text = scan_path.read_text(encoding="utf-8")
    risky = []
    if "rglob(" in text or "os.walk(" in text:
        risky.append("full tree walk detected")
    if risky:
        state.add("scan_allowlist", WARNING, f"scan script review needed: {risky}")
    else:
        state.add("scan_allowlist", PASS, "scan script uses pattern-based allowlist collection")


def check_protocol_round1_api_ban(state: GateState, root: Path) -> None:
    protocol = load_yaml(root / "repo_protocol_standard.yaml")
    safety = protocol.get("safety", {})
    if safety.get("allow_external_api_in_round_1") is False:
        state.add("protocol_round1_api", PASS, "Round 1 external API ban present in protocol")
    else:
        state.add("protocol_round1_api", WARNING, "allow_external_api_in_round_1 not set to false")


def check_requirements_dev_playwright(state: GateState, root: Path) -> None:
    path = root / "requirements-dev.txt"
    if not path.exists():
        state.add("requirements_dev", WARNING, "requirements-dev.txt missing")
        return
    text = path.read_text(encoding="utf-8").lower()
    if "playwright" in text and "pytest" in text:
        state.add("requirements_dev", PASS, "requirements-dev.txt includes playwright and pytest")
    elif "playwright" in text:
        state.add("requirements_dev", WARNING, "pytest not listed in requirements-dev.txt")
    else:
        state.add("requirements_dev", WARNING, "playwright not listed in requirements-dev.txt")


def check_installation_doc(state: GateState, root: Path) -> None:
    path = root / "docs" / "installation.md"
    if not path.exists():
        state.add("installation_doc", BLOCKED, "docs/installation.md missing")
        return
    text = path.read_text(encoding="utf-8")
    required = ["agent_gate.py", "scan_repos.py", "ui_check.py"]
    missing = [item for item in required if item not in text]
    if missing:
        state.add("installation_doc", WARNING, f"installation.md missing commands: {missing}")
    else:
        state.add("installation_doc", PASS, "installation.md covers core refresh commands")


def check_example_fixtures(state: GateState, root: Path) -> None:
    fixtures = [
        "data/repo_snapshots.example.json",
        "data/repo_status.example.json",
        "config/repos.example.yaml",
    ]
    missing = [item for item in fixtures if not (root / item).exists()]
    if missing:
        state.add("example_fixtures", WARNING, f"example fixtures missing: {missing}")
    else:
        state.add("example_fixtures", PASS, "example data fixtures present")


def check_pytest_tests(state: GateState, root: Path) -> None:
    tests_dir = root / "tests"
    test_files = sorted(tests_dir.glob("test_*.py")) if tests_dir.is_dir() else []
    if len(test_files) < 2:
        state.add("pytest_tests", WARNING, "tests/ should contain at least two test modules")
        return
    state.add("pytest_tests", PASS, f"pytest tests present ({len(test_files)} modules)")


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
    check_round_docs_exist(state, root)
    check_round_doc_sections(state, root)
    check_ui_check_script(state, root)
    check_audit_report(state, root)
    check_playwright_local_only(state, root)
    check_scan_allowlist_compliance(state, root)
    check_protocol_round1_api_ban(state, root)
    check_requirements_dev_playwright(state, root)
    check_installation_doc(state, root)
    check_example_fixtures(state, root)
    check_pytest_tests(state, root)
    report = render_report(state, root)

    print(f"[gate] verdict={state.verdict} report={report}")
    for item in state.findings:
        print(f"[{item.severity}] {item.check}: {item.message}")
    return EXIT_CODES[state.verdict]


if __name__ == "__main__":
    raise SystemExit(main())
