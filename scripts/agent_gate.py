#!/usr/bin/env python3
"""Deterministic safety gate for repo-ops-dashboard."""

from __future__ import annotations

import argparse
import json
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
    "round_25_architecture_absorption_personal_agent_os_upgrade.md",
    "round_26_project_registry_mvp.md",
    "round_27_portfolio_state_snapshot.md",
    "round_28_governance_task_queue.md",
    "round_29_proof_of_work_system.md",
    "round_30_agent_run_jsonl_audit_trail.md",
    "round_31_review_queue_mvp.md",
    "round_32_execpolicy_checker.md",
    "round_33_repo_context_index_mvp.md",
    "round_34_readonly_repo_scanner_v2.md",
    "round_35_status_analyzer_v2.md",
    "round_36_priority_scoring_system.md",
    "round_37_lifecycle_rules.md",
    "round_38_blocker_management.md",
    "round_39_dashboard_v2.md",
    "round_40_playwright_dashboard_validation.md",
    "round_41_prompt_generator_for_cursor.md",
    "round_42_prompt_generator_for_codex.md",
    "round_43_openclaw_orchestration_bridge.md",
    "round_44_weekly_digest_mvp.md",
    "round_45_daily_briefing_mvp.md",
    "round_46_eval_registry_script.md",
    "round_47_handoff_protocol_implementation.md",
    "round_48_failure_recovery_retry_policy.md",
    "round_49_checkpoint_snapshot.md",
    "round_50_skill_playbook_candidate_extraction.md",
    "round_51_project_rule_promotion.md",
    "round_52_cross_repo_protocol_sync_suggestion.md",
    "round_53_budget_cost_tracking.md",
    "round_54_wip_limit_scheduling.md",
    "round_55_feishu_lark_notification_planning.md",
    "round_56_feishu_lark_notification_mvp.md",
    "round_57_mac_local_notification.md",
    "round_58_openclaw_daily_briefing_skill.md",
    "round_59_browser_dashboard_interaction.md",
    "round_60_multi_agent_handoff_trial.md",
    "round_61_portfolio_governance_hardening.md",
    "round_62_release_backup_restore.md",
    "round_63_personal_agent_os_long_term_integration.md",
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
        "governance/README.md",
        "governance/task_specs/task_spec.template.yaml",
        "governance/proof_of_work/proof_of_work.template.json",
        "governance/review_queue.yaml",
        "governance/review_queue.example.yaml",
        "governance/repo_context_index.example.yaml",
        "governance/scan_policy.example.yaml",
        "governance/analyzer_policy.example.yaml",
        "governance/priority_scoring_policy.example.yaml",
        "governance/lifecycle_policy.example.yaml",
        "governance/execpolicy/portfolio.rules",
        "governance/evals/registry.yaml",
        "docs/roadmap_40_rounds.md",
    ]
    missing = [item for item in required if not (root / item).exists()]
    if missing:
        state.add("required_files", BLOCKED, f"missing required files: {missing}")
    else:
        state.add("required_files", PASS, "required governance files exist")


ALLOWED_ENV_TRACKED = {".env.example"}


def check_env_git_risk(state: GateState, root: Path) -> None:
    tracked = run_git_lines(["git", "ls-files", ".env", ".env.*"], root)
    tracked = [path for path in tracked if path not in ALLOWED_ENV_TRACKED]
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
    allowed_feishu_scripts = {
        "prepare_feishu_payload.py",
        "sync_feishu_bitable.py",
        "plan_feishu_notifications.py",
        "validate_feishu_notification_policy.py",
        "send_feishu_notification.py",
    }
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
        state.add("round_docs", PASS, "round docs 00-63 exist")


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


def check_ui_check_http(state: GateState, root: Path) -> None:
    script = root / "scripts" / "ui_check_http.sh"
    ui_check = root / "scripts" / "ui_check.py"
    if not script.exists():
        state.add("ui_check_http", WARNING, "scripts/ui_check_http.sh missing")
        return
    text = script.read_text(encoding="utf-8")
    ui_text = ui_check.read_text(encoding="utf-8") if ui_check.exists() else ""
    if "127.0.0.1" in text and "http.server" in text and "repo_card_state_attrs" in ui_text:
        state.add("ui_check_http", PASS, "HTTP dashboard ui_check wired (127.0.0.1 only)")
    else:
        state.add("ui_check_http", WARNING, "ui_check_http incomplete or card state check missing")


def check_audit_report(state: GateState, root: Path) -> None:
    path = root / "reports" / "round_25_architecture_absorption_audit_report.md"
    if not path.exists():
        state.add("audit_report", WARNING, "reports/round_25_architecture_absorption_audit_report.md missing")
    else:
        state.add("audit_report", PASS, "round 25 architecture absorption audit report exists")


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


def check_scan_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "scan_policy.yaml"
    example = root / "governance" / "scan_policy.example.yaml"
    if not live.exists():
        state.add("scan_policy", BLOCKED, "config/scan_policy.yaml missing")
        return
    if not example.exists():
        state.add("scan_policy", BLOCKED, "governance/scan_policy.example.yaml missing")
        return
    try:
        from validate_scan_policy import read_scan_policy, summarize_scan_policy, validate_scan_policy
    except ImportError:
        state.add("scan_policy", BLOCKED, "validate_scan_policy module unavailable")
        return
    try:
        data = read_scan_policy(live)
    except FileNotFoundError as exc:
        state.add("scan_policy", BLOCKED, str(exc))
        return
    errors = validate_scan_policy(data, live.name)
    if errors:
        state.add("scan_policy", BLOCKED, f"scan_policy.yaml invalid: {errors[0]}")
        return
    summary = summarize_scan_policy(data)
    scan_path = root / "scripts" / "scan_repos.py"
    if scan_path.exists() and "SCANNER_VERSION" in scan_path.read_text(encoding="utf-8"):
        state.add(
            "scan_policy",
            PASS,
            f"scan_policy v2 valid ({summary.get('pattern_count')} patterns, scanner {summary.get('scanner_version')})",
        )
    else:
        state.add("scan_policy", WARNING, "scan_policy valid but scan_repos.py missing SCANNER_VERSION marker")


def check_analyzer_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "analyzer_policy.yaml"
    example = root / "governance" / "analyzer_policy.example.yaml"
    if not live.exists():
        state.add("analyzer_policy", BLOCKED, "config/analyzer_policy.yaml missing")
        return
    if not example.exists():
        state.add("analyzer_policy", BLOCKED, "governance/analyzer_policy.example.yaml missing")
        return
    try:
        from validate_analyzer_policy import read_analyzer_policy, summarize_analyzer_policy, validate_analyzer_policy
    except ImportError:
        state.add("analyzer_policy", BLOCKED, "validate_analyzer_policy module unavailable")
        return
    try:
        data = read_analyzer_policy(live)
    except FileNotFoundError as exc:
        state.add("analyzer_policy", BLOCKED, str(exc))
        return
    errors = validate_analyzer_policy(data, live.name)
    if errors:
        state.add("analyzer_policy", BLOCKED, f"analyzer_policy.yaml invalid: {errors[0]}")
        return
    summary = summarize_analyzer_policy(data)
    analyze_path = root / "scripts" / "analyze_repos.py"
    if analyze_path.exists() and "ANALYZER_VERSION" in analyze_path.read_text(encoding="utf-8"):
        state.add(
            "analyzer_policy",
            PASS,
            f"analyzer_policy v2 valid ({len(summary.get('dimensions', []))} dimensions, analyzer {summary.get('analyzer_version')})",
        )
    else:
        state.add("analyzer_policy", WARNING, "analyzer_policy valid but analyze_repos.py missing ANALYZER_VERSION marker")


def check_priority_scoring_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "priority_scoring_policy.yaml"
    example = root / "governance" / "priority_scoring_policy.example.yaml"
    if not live.exists():
        state.add("priority_scoring_policy", BLOCKED, "config/priority_scoring_policy.yaml missing")
        return
    if not example.exists():
        state.add("priority_scoring_policy", BLOCKED, "governance/priority_scoring_policy.example.yaml missing")
        return
    try:
        from validate_priority_scoring_policy import (
            read_priority_scoring_policy,
            summarize_priority_scoring_policy,
            validate_priority_scoring_policy,
        )
    except ImportError:
        state.add("priority_scoring_policy", BLOCKED, "validate_priority_scoring_policy module unavailable")
        return
    try:
        data = read_priority_scoring_policy(live)
    except FileNotFoundError as exc:
        state.add("priority_scoring_policy", BLOCKED, str(exc))
        return
    errors = validate_priority_scoring_policy(data, live.name)
    if errors:
        state.add("priority_scoring_policy", BLOCKED, f"priority_scoring_policy.yaml invalid: {errors[0]}")
        return
    summary = summarize_priority_scoring_policy(data)
    scoring_path = root / "scripts" / "priority_scoring.py"
    if scoring_path.exists():
        state.add(
            "priority_scoring_policy",
            PASS,
            f"priority_scoring_policy v1 valid ({len(summary.get('factors', []))} factors, scale {summary.get('product_scale')})",
        )
    else:
        state.add("priority_scoring_policy", WARNING, "priority_scoring_policy valid but priority_scoring.py missing")


def check_lifecycle_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "lifecycle_policy.yaml"
    example = root / "governance" / "lifecycle_policy.example.yaml"
    if not live.exists():
        state.add("lifecycle_policy", BLOCKED, "config/lifecycle_policy.yaml missing")
        return
    if not example.exists():
        state.add("lifecycle_policy", BLOCKED, "governance/lifecycle_policy.example.yaml missing")
        return
    try:
        from validate_lifecycle_policy import read_lifecycle_policy, summarize_lifecycle_policy, validate_lifecycle_policy
    except ImportError:
        state.add("lifecycle_policy", BLOCKED, "validate_lifecycle_policy module unavailable")
        return
    try:
        data = read_lifecycle_policy(live)
    except FileNotFoundError as exc:
        state.add("lifecycle_policy", BLOCKED, str(exc))
        return
    errors = validate_lifecycle_policy(data, live.name)
    if errors:
        state.add("lifecycle_policy", BLOCKED, f"lifecycle_policy.yaml invalid: {errors[0]}")
        return
    summary = summarize_lifecycle_policy(data)
    analyze_path = root / "scripts" / "analyze_repos.py"
    if analyze_path.exists() and "derive_lifecycle_v1" in analyze_path.read_text(encoding="utf-8"):
        state.add(
            "lifecycle_policy",
            PASS,
            f"lifecycle_policy v1 valid ({summary.get('state_count')} states)",
        )
    else:
        state.add("lifecycle_policy", WARNING, "lifecycle_policy valid but derive_lifecycle_v1 not wired in analyze_repos.py")


def check_openclaw_orchestration_bridge(state: GateState, root: Path) -> None:
    script = root / "scripts" / "openclaw_orchestration_bridge.py"
    manifest = root / "governance" / "openclaw_orchestration.manifest.yaml"
    template = root / "prompts" / "openclaw_orchestration_brief.md"
    if not script.exists() or not manifest.exists() or not template.exists():
        state.add("openclaw_orchestration_bridge", WARNING, "OpenClaw bridge script/manifest/template missing")
        return
    text = script.read_text(encoding="utf-8")
    if "--dry-run" in text and "external_api_called" in text:
        state.add("openclaw_orchestration_bridge", PASS, "OpenClaw orchestration bridge wired (dry-run default)")
    else:
        state.add("openclaw_orchestration_bridge", WARNING, "OpenClaw bridge missing dry-run or safety markers")


def check_weekly_digest(state: GateState, root: Path) -> None:
    script = root / "scripts" / "generate_weekly_digest.py"
    template = root / "prompts" / "weekly_digest.md"
    if not script.exists() or not template.exists():
        state.add("weekly_digest", WARNING, "generate_weekly_digest.py or weekly_digest template missing")
        return
    text = script.read_text(encoding="utf-8")
    if "governance/digests/weekly" in text and "--dry-run" in text:
        state.add("weekly_digest", PASS, "weekly_digest generator wired")
    else:
        state.add("weekly_digest", WARNING, "weekly_digest generator incomplete")


def check_daily_briefing(state: GateState, root: Path) -> None:
    script = root / "scripts" / "generate_daily_briefing.py"
    template = root / "prompts" / "daily_briefing.md"
    if not script.exists() or not template.exists():
        state.add("daily_briefing", WARNING, "generate_daily_briefing.py or daily_briefing template missing")
        return
    text = script.read_text(encoding="utf-8")
    if "review_queue" in text and "governance/digests/daily" in text:
        state.add("daily_briefing", PASS, "daily_briefing generator wired")
    else:
        state.add("daily_briefing", WARNING, "daily_briefing generator incomplete")


def check_openclaw_daily_briefing_skill(state: GateState, root: Path) -> None:
    script = root / "scripts" / "openclaw_daily_briefing_skill.py"
    template = root / "prompts" / "openclaw_daily_briefing_skill.md"
    skill_doc = root / "skills" / "openclaw_repo_ops" / "SKILL.md"
    if not script.exists() or not template.exists():
        state.add("openclaw_daily_briefing_skill", WARNING, "openclaw_daily_briefing_skill script/template missing")
        return
    text = script.read_text(encoding="utf-8")
    skill_text = skill_doc.read_text(encoding="utf-8") if skill_doc.exists() else ""
    if (
        "--dry-run" in text
        and "external_api_called" in text
        and "repo_status" in text
        and "openclaw_daily_briefing_skill" in skill_text
    ):
        state.add("openclaw_daily_briefing_skill", PASS, "OpenClaw daily briefing skill wired (digest + repo_status)")
    else:
        state.add("openclaw_daily_briefing_skill", WARNING, "OpenClaw daily briefing skill incomplete")


def check_handoff_trial(state: GateState, root: Path) -> None:
    script = root / "scripts" / "run_handoff_trial.py"
    policy = root / "governance" / "handoffs" / "handoff_trial_policy.yaml"
    task_spec = root / "governance" / "task_specs" / "example_handoff_trial_task_spec.yaml"
    if not script.exists() or not policy.exists() or not task_spec.exists():
        state.add("handoff_trial", WARNING, "handoff trial script/policy/task_spec missing")
        return
    text = script.read_text(encoding="utf-8")
    if "--dry-run" in text and "proof_of_work" in text and "openclaw_daily_briefing_skill" in text:
        state.add("handoff_trial", PASS, "multi-agent handoff trial wired (dry-run default)")
    else:
        state.add("handoff_trial", WARNING, "handoff trial incomplete")


def check_governance_hardening(state: GateState, root: Path) -> None:
    script = root / "scripts" / "audit_governance_hardening.py"
    policy = root / "config" / "governance_hardening_policy.yaml"
    example = root / "governance" / "governance_hardening_policy.example.yaml"
    if not script.exists() or not policy.exists():
        state.add("governance_hardening", WARNING, "governance hardening audit script/policy missing")
        return
    text = script.read_text(encoding="utf-8")
    if "--write" in text and "denylist" in text and example.exists():
        state.add("governance_hardening", PASS, "governance hardening audit wired (dry-run default)")
    else:
        state.add("governance_hardening", WARNING, "governance hardening audit incomplete")


def check_backup_restore(state: GateState, root: Path) -> None:
    script = root / "scripts" / "backup_governance_state.py"
    policy = root / "config" / "backup_restore_policy.yaml"
    doc = root / "docs" / "backup_restore.md"
    if not script.exists() or not policy.exists() or not doc.exists():
        state.add("backup_restore", WARNING, "backup/restore script/policy/doc missing")
        return
    text = script.read_text(encoding="utf-8")
    if "--write" in text and "hitl" in doc.read_text(encoding="utf-8").lower():
        state.add("backup_restore", PASS, "governance backup/restore wired (dry-run default, HITL restore)")
    else:
        state.add("backup_restore", WARNING, "backup/restore incomplete")


def check_personal_os_integration(state: GateState, root: Path) -> None:
    script = root / "scripts" / "personal_os_integration_snapshot.py"
    policy = root / "config" / "personal_os_integration_policy.yaml"
    example = root / "governance" / "personal_os_integration.example.yaml"
    if not script.exists() or not policy.exists():
        state.add("personal_os_integration", WARNING, "personal OS integration script/policy missing")
        return
    text = script.read_text(encoding="utf-8")
    if "mock_modules" in text and "architecture_40_rounds_complete" in text and example.exists():
        state.add("personal_os_integration", PASS, "Personal Agent OS integration snapshot wired (mock/dry-run)")
    else:
        state.add("personal_os_integration", WARNING, "personal OS integration incomplete")


def check_codex_task_spec_prompt(state: GateState, root: Path) -> None:
    script = root / "scripts" / "generate_codex_prompt_from_task_spec.py"
    template = root / "prompts" / "codex_from_task_spec.md"
    example = root / "governance" / "task_specs" / "example_codex_task_spec.yaml"
    if not script.exists():
        state.add("codex_task_spec_prompt", WARNING, "generate_codex_prompt_from_task_spec.py missing")
        return
    if not template.exists() or not example.exists():
        state.add("codex_task_spec_prompt", WARNING, "codex_from_task_spec template or example task_spec missing")
        return
    text = script.read_text(encoding="utf-8")
    if "validate_task_spec" in text and "Codex" in text:
        state.add("codex_task_spec_prompt", PASS, "Codex task_spec prompt generator wired")
    else:
        state.add("codex_task_spec_prompt", WARNING, "Codex task_spec prompt generator incomplete")


def check_cursor_task_spec_prompt(state: GateState, root: Path) -> None:
    script = root / "scripts" / "generate_cursor_prompt_from_task_spec.py"
    template = root / "prompts" / "cursor_from_task_spec.md"
    example = root / "governance" / "task_specs" / "example_task_spec.yaml"
    if not script.exists():
        state.add("cursor_task_spec_prompt", WARNING, "generate_cursor_prompt_from_task_spec.py missing")
        return
    if not template.exists() or not example.exists():
        state.add("cursor_task_spec_prompt", WARNING, "cursor_from_task_spec template or example task_spec missing")
        return
    text = script.read_text(encoding="utf-8")
    if "validate_task_spec" in text and "assigned_agent" in text:
        state.add("cursor_task_spec_prompt", PASS, "Cursor task_spec prompt generator wired")
    else:
        state.add("cursor_task_spec_prompt", WARNING, "Cursor task_spec prompt generator incomplete")


def check_ui_check_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "ui_check_policy.yaml"
    example = root / "governance" / "ui_check_policy.example.yaml"
    if not live.exists():
        state.add("ui_check_policy", BLOCKED, "config/ui_check_policy.yaml missing")
        return
    if not example.exists():
        state.add("ui_check_policy", BLOCKED, "governance/ui_check_policy.example.yaml missing")
        return
    try:
        from validate_ui_check_policy import read_ui_check_policy, summarize_ui_check_policy, validate_ui_check_policy
    except ImportError:
        state.add("ui_check_policy", BLOCKED, "validate_ui_check_policy module unavailable")
        return
    try:
        data = read_ui_check_policy(live)
    except FileNotFoundError as exc:
        state.add("ui_check_policy", BLOCKED, str(exc))
        return
    errors = validate_ui_check_policy(data, live.name)
    if errors:
        state.add("ui_check_policy", BLOCKED, f"ui_check_policy.yaml invalid: {errors[0]}")
        return
    summary = summarize_ui_check_policy(data)
    ui_path = root / "scripts" / "ui_check.py"
    if ui_path.exists() and "console_no_errors" in ui_path.read_text(encoding="utf-8"):
        state.add(
            "ui_check_policy",
            PASS,
            f"ui_check_policy v1 valid ({summary.get('required_check_count')} required checks)",
        )
    else:
        state.add("ui_check_policy", WARNING, "ui_check_policy valid but console checks not wired in ui_check.py")


def check_mac_notification_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "mac_notification_policy.yaml"
    example = root / "governance" / "mac_notification_policy.example.yaml"
    sender = root / "scripts" / "send_mac_notification.py"
    validator = root / "scripts" / "validate_mac_notification_policy.py"
    output = root / "reports" / "mac_notification_payload.json"
    if not live.exists() or not validator.exists():
        state.add("mac_notification_policy", BLOCKED, "mac_notification_policy.yaml or validator missing")
        return
    try:
        from validate_mac_notification_policy import load_yaml, validate_mac_notification_policy
    except ImportError:
        state.add("mac_notification_policy", BLOCKED, "validate_mac_notification_policy unavailable")
        return
    errors = validate_mac_notification_policy(load_yaml(live), live.name)
    if errors:
        state.add("mac_notification_policy", BLOCKED, f"mac_notification_policy invalid: {errors[0]}")
        return
    if example.exists() and sender.exists() and output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
        status = payload.get("delivery", {}).get("status", "unknown")
        state.add(
            "mac_notification_policy",
            PASS,
            f"Mac local notification wired (payload={status}, osascript opt-in)",
        )
    else:
        state.add(
            "mac_notification_policy",
            WARNING,
            "mac_notification_policy valid but sender/output incomplete",
        )


def check_feishu_notification_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "feishu_notification_policy.yaml"
    example = root / "governance" / "feishu_notification_policy.example.yaml"
    planner = root / "scripts" / "plan_feishu_notifications.py"
    sender = root / "scripts" / "send_feishu_notification.py"
    validator = root / "scripts" / "validate_feishu_notification_policy.py"
    output = root / "governance" / "feishu_notification_plan.yaml"
    outbound = root / "reports" / "feishu_outbound_preview.json"
    if not live.exists() or not validator.exists():
        state.add("feishu_notification_policy", BLOCKED, "feishu_notification_policy.yaml or validator missing")
        return
    try:
        from validate_feishu_notification_policy import load_yaml, validate_feishu_notification_policy
    except ImportError:
        state.add("feishu_notification_policy", BLOCKED, "validate_feishu_notification_policy unavailable")
        return
    errors = validate_feishu_notification_policy(load_yaml(live), live.name)
    if errors:
        state.add("feishu_notification_policy", BLOCKED, f"feishu_notification_policy invalid: {errors[0]}")
        return
    if example.exists() and planner.exists() and output.exists() and sender.exists() and outbound.exists():
        summary = load_yaml(output).get("summary", {})
        outbound_record = json.loads(outbound.read_text(encoding="utf-8"))
        delivery = outbound_record.get("delivery", {}).get("status", "unknown")
        state.add(
            "feishu_notification_policy",
            PASS,
            f"Feishu notification MVP wired (sources={summary.get('sources_ready', 0)}/{summary.get('sources_total', 0)}, outbound={delivery})",
        )
    elif example.exists() and planner.exists() and output.exists():
        summary = load_yaml(output).get("summary", {})
        state.add(
            "feishu_notification_policy",
            PASS,
            f"Feishu notification planning wired (sources={summary.get('sources_ready', 0)}/{summary.get('sources_total', 0)}, no API)",
        )
    else:
        state.add(
            "feishu_notification_policy",
            WARNING,
            "feishu_notification_policy valid but planner/output incomplete",
        )


def check_wip_limit_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "wip_limit_policy.yaml"
    example = root / "governance" / "wip_limit_policy.example.yaml"
    checker = root / "scripts" / "check_wip_limit.py"
    validator = root / "scripts" / "validate_wip_limit_policy.py"
    output = root / "governance" / "wip_limit_status.yaml"
    if not live.exists() or not validator.exists():
        state.add("wip_limit_policy", BLOCKED, "wip_limit_policy.yaml or validator missing")
        return
    try:
        from validate_wip_limit_policy import load_yaml, validate_wip_limit_policy
    except ImportError:
        state.add("wip_limit_policy", BLOCKED, "validate_wip_limit_policy unavailable")
        return
    errors = validate_wip_limit_policy(load_yaml(live), live.name)
    if errors:
        state.add("wip_limit_policy", BLOCKED, f"wip_limit_policy invalid: {errors[0]}")
        return
    if example.exists() and checker.exists() and output.exists():
        summary = load_yaml(output).get("summary", {})
        state.add(
            "wip_limit_policy",
            PASS,
            f"WIP limit scheduling wired (effective_wip={summary.get('effective_wip', 0)}, read-only)",
        )
    else:
        state.add(
            "wip_limit_policy",
            WARNING,
            "wip_limit_policy valid but checker/output incomplete",
        )


def check_budget_tracking_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "budget_tracking_policy.yaml"
    example = root / "governance" / "budget_tracking_policy.example.yaml"
    tracker = root / "scripts" / "track_budget_cost.py"
    validator = root / "scripts" / "validate_budget_tracking_policy.py"
    output = root / "governance" / "budget_cost_tracking.yaml"
    if not live.exists() or not validator.exists():
        state.add("budget_tracking_policy", BLOCKED, "budget_tracking_policy.yaml or validator missing")
        return
    try:
        from validate_budget_tracking_policy import load_yaml, validate_budget_tracking_policy
    except ImportError:
        state.add("budget_tracking_policy", BLOCKED, "validate_budget_tracking_policy unavailable")
        return
    errors = validate_budget_tracking_policy(load_yaml(live), live.name)
    if errors:
        state.add("budget_tracking_policy", BLOCKED, f"budget_tracking_policy invalid: {errors[0]}")
        return
    if example.exists() and tracker.exists() and output.exists():
        summary = load_yaml(output).get("summary", {})
        warnings = summary.get("projects_with_warning", 0)
        state.add(
            "budget_tracking_policy",
            PASS,
            f"budget cost tracking wired (mock estimates, {warnings} warning(s))",
        )
    else:
        state.add(
            "budget_tracking_policy",
            WARNING,
            "budget_tracking_policy valid but tracker/output incomplete",
        )


def check_protocol_sync_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "protocol_sync_policy.yaml"
    example = root / "governance" / "protocol_sync_policy.example.yaml"
    reporter = root / "scripts" / "protocol_sync_report.py"
    validator = root / "scripts" / "validate_protocol_sync_policy.py"
    yaml_out = root / "governance" / "protocol_sync_suggestions.yaml"
    if not live.exists() or not validator.exists():
        state.add("protocol_sync_policy", BLOCKED, "protocol_sync_policy.yaml or validator missing")
        return
    try:
        from validate_protocol_sync_policy import load_yaml, validate_protocol_sync_policy
    except ImportError:
        state.add("protocol_sync_policy", BLOCKED, "validate_protocol_sync_policy unavailable")
        return
    errors = validate_protocol_sync_policy(load_yaml(live), live.name)
    if errors:
        state.add("protocol_sync_policy", BLOCKED, f"protocol_sync_policy invalid: {errors[0]}")
        return
    if example.exists() and reporter.exists() and yaml_out.exists():
        suggestions = load_yaml(yaml_out).get("suggestions", [])
        need_sync = sum(1 for s in suggestions if s.get("action") == "sync_suggested")
        state.add(
            "protocol_sync_policy",
            PASS,
            f"protocol sync suggestions wired ({need_sync} repo(s) need sync, read-only)",
        )
    else:
        state.add(
            "protocol_sync_policy",
            WARNING,
            "protocol_sync_policy valid but reporter/yaml output incomplete",
        )


def check_project_rule_promotion_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "project_rule_promotion_policy.yaml"
    example = root / "governance" / "project_rule_promotion_policy.example.yaml"
    promoter = root / "scripts" / "promote_project_rule.py"
    validator = root / "scripts" / "validate_project_rule_promotion_policy.py"
    queue = root / "governance" / "project_rule_promotion_queue.yaml"
    if not live.exists() or not validator.exists():
        state.add("project_rule_promotion_policy", BLOCKED, "project_rule_promotion_policy.yaml or validator missing")
        return
    try:
        from validate_project_rule_promotion_policy import (
            load_yaml,
            validate_project_rule_promotion_policy,
        )
    except ImportError:
        state.add("project_rule_promotion_policy", BLOCKED, "validate_project_rule_promotion_policy unavailable")
        return
    errors = validate_project_rule_promotion_policy(load_yaml(live), live.name)
    if errors:
        state.add("project_rule_promotion_policy", BLOCKED, f"project_rule_promotion_policy invalid: {errors[0]}")
        return
    if example.exists() and promoter.exists() and queue.exists():
        proposals = load_yaml(queue).get("proposals", [])
        state.add(
            "project_rule_promotion_policy",
            PASS,
            f"project rule promotion wired ({len(proposals)} proposal(s), HITL merge)",
        )
    else:
        state.add(
            "project_rule_promotion_policy",
            WARNING,
            "project_rule_promotion_policy valid but promoter/queue incomplete",
        )


def check_playbook_extraction_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "playbook_extraction_policy.yaml"
    example = root / "governance" / "playbook_extraction_policy.example.yaml"
    extractor = root / "scripts" / "extract_playbook_candidates.py"
    validator = root / "scripts" / "validate_playbook_extraction_policy.py"
    registry = root / "governance" / "playbook_candidates.yaml"
    if not live.exists() or not validator.exists():
        state.add("playbook_extraction_policy", BLOCKED, "playbook_extraction_policy.yaml or validator missing")
        return
    try:
        from validate_playbook_extraction_policy import (
            load_yaml,
            validate_playbook_extraction_policy,
        )
    except ImportError:
        state.add("playbook_extraction_policy", BLOCKED, "validate_playbook_extraction_policy unavailable")
        return
    errors = validate_playbook_extraction_policy(load_yaml(live), live.name)
    if errors:
        state.add("playbook_extraction_policy", BLOCKED, f"playbook_extraction_policy invalid: {errors[0]}")
        return
    if example.exists() and extractor.exists() and registry.exists():
        candidates = load_yaml(registry).get("candidates", [])
        state.add(
            "playbook_extraction_policy",
            PASS,
            f"playbook candidate extraction wired ({len(candidates)} candidate(s), dry-run)",
        )
    else:
        state.add("playbook_extraction_policy", WARNING, "playbook_extraction_policy valid but extractor/registry incomplete")


def check_checkpoint_snapshot_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "checkpoint_snapshot_policy.yaml"
    example = root / "governance" / "checkpoint_snapshot_policy.example.yaml"
    planner = root / "scripts" / "snapshot_portfolio_checkpoint.py"
    validator = root / "scripts" / "validate_checkpoint_snapshot_policy.py"
    manifest = root / "governance" / "checkpoints" / "manifest.yaml"
    if not live.exists() or not validator.exists():
        state.add("checkpoint_snapshot_policy", BLOCKED, "checkpoint_snapshot_policy.yaml or validator missing")
        return
    try:
        from validate_checkpoint_snapshot_policy import (
            load_yaml,
            validate_checkpoint_snapshot_policy,
        )
    except ImportError:
        state.add("checkpoint_snapshot_policy", BLOCKED, "validate_checkpoint_snapshot_policy unavailable")
        return
    errors = validate_checkpoint_snapshot_policy(load_yaml(live), live.name)
    if errors:
        state.add("checkpoint_snapshot_policy", BLOCKED, f"checkpoint_snapshot_policy invalid: {errors[0]}")
        return
    if example.exists() and planner.exists() and manifest.exists():
        state.add("checkpoint_snapshot_policy", PASS, "portfolio checkpoint snapshot policy wired (dry-run)")
    else:
        state.add(
            "checkpoint_snapshot_policy",
            WARNING,
            "checkpoint_snapshot_policy valid but planner/example/manifest incomplete",
        )


def check_failure_recovery_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "failure_recovery_policy.yaml"
    example = root / "governance" / "failure_recovery_policy.example.yaml"
    planner = root / "scripts" / "failure_recovery.py"
    validator = root / "scripts" / "validate_failure_recovery_policy.py"
    if not live.exists() or not validator.exists():
        state.add("failure_recovery_policy", BLOCKED, "failure_recovery_policy.yaml or validator missing")
        return
    try:
        from validate_failure_recovery_policy import (
            load_yaml,
            validate_failure_recovery_policy,
        )
    except ImportError:
        state.add("failure_recovery_policy", BLOCKED, "validate_failure_recovery_policy unavailable")
        return
    errors = validate_failure_recovery_policy(load_yaml(live), live.name)
    if errors:
        state.add("failure_recovery_policy", BLOCKED, f"failure_recovery_policy invalid: {errors[0]}")
        return
    if example.exists() and planner.exists() and "plan_recovery" in planner.read_text(encoding="utf-8"):
        state.add("failure_recovery_policy", PASS, "failure recovery policy and planner wired (dry-run)")
    else:
        state.add("failure_recovery_policy", WARNING, "failure_recovery_policy valid but planner/example incomplete")


def check_blocker_policy(state: GateState, root: Path) -> None:
    live = root / "config" / "blocker_policy.yaml"
    example = root / "governance" / "blocker_policy.example.yaml"
    if not live.exists():
        state.add("blocker_policy", BLOCKED, "config/blocker_policy.yaml missing")
        return
    if not example.exists():
        state.add("blocker_policy", BLOCKED, "governance/blocker_policy.example.yaml missing")
        return
    try:
        from validate_blocker_policy import read_blocker_policy, summarize_blocker_policy, validate_blocker_policy
    except ImportError:
        state.add("blocker_policy", BLOCKED, "validate_blocker_policy module unavailable")
        return
    try:
        data = read_blocker_policy(live)
    except FileNotFoundError as exc:
        state.add("blocker_policy", BLOCKED, str(exc))
        return
    errors = validate_blocker_policy(data, live.name)
    if errors:
        state.add("blocker_policy", BLOCKED, f"blocker_policy.yaml invalid: {errors[0]}")
        return
    summary = summarize_blocker_policy(data)
    mgmt_path = root / "scripts" / "blocker_management.py"
    analyze_path = root / "scripts" / "analyze_repos.py"
    if mgmt_path.exists() and analyze_path.exists() and "blocker_details" in analyze_path.read_text(encoding="utf-8"):
        state.add(
            "blocker_policy",
            PASS,
            f"blocker_policy v1 valid ({summary.get('type_count')} types, {len(summary.get('escalation_levels', []))} escalation levels)",
        )
    else:
        state.add("blocker_policy", WARNING, "blocker_policy valid but blocker_details not wired in analyze_repos.py")


def check_protocol_governance_api_ban(state: GateState, root: Path) -> None:
    protocol = load_yaml(root / "repo_protocol_standard.yaml")
    safety = protocol.get("safety", {})
    if safety.get("allow_external_api_in_governance_round") is False:
        state.add("protocol_governance_api", PASS, "governance round external API ban present in protocol")
    else:
        state.add("protocol_governance_api", WARNING, "allow_external_api_in_governance_round not set to false")


def check_protocol_version(state: GateState, root: Path) -> None:
    protocol = load_yaml(root / "repo_protocol_standard.yaml")
    version = str(protocol.get("protocol_version", ""))
    project_type = str(protocol.get("project_type", ""))
    positioning = protocol.get("project_positioning", {})
    if version >= "0.3.0" and project_type == "personal_portfolio_orchestrator":
        state.add("protocol_version", PASS, "protocol v0.3.0 portfolio governance positioning present")
    else:
        state.add("protocol_version", BLOCKED, f"unexpected protocol version/type: {version}/{project_type}")
    if positioning.get("role") != "personal_agent_os_governance_layer":
        state.add("protocol_positioning", WARNING, "project_positioning.role is not personal_agent_os_governance_layer")
    else:
        state.add("protocol_positioning", PASS, "Personal Agent OS positioning present")


def check_project_registry(state: GateState, root: Path) -> None:
    path = root / "governance" / "project_registry.yaml"
    if not path.exists():
        state.add("project_registry", BLOCKED, "governance/project_registry.yaml missing")
        return
    data = load_yaml(path)
    projects = list(data.get("projects", []))
    if not projects:
        state.add("project_registry", BLOCKED, "project_registry.yaml has no projects")
        return
    required_fields = (
        "project_id",
        "repo_name",
        "path",
        "domain",
        "lifecycle",
        "owner",
        "default_agent",
        "governance_level",
    )
    incomplete = []
    for project in projects:
        pid = str(project.get("project_id", "?"))
        missing = [field for field in required_fields if not project.get(field)]
        if missing:
            incomplete.append(f"{pid}: {missing}")
    repos_cfg = load_yaml(root / "config" / "repos.yaml")
    repo_count = len(repos_cfg.get("repos", []))
    if incomplete:
        state.add("project_registry", BLOCKED, f"incomplete project entries: {incomplete[:3]}")
    elif len(projects) < repo_count:
        state.add(
            "project_registry",
            WARNING,
            f"registry has {len(projects)} projects but repos.yaml has {repo_count}",
        )
    else:
        state.add(
            "project_registry",
            PASS,
            f"project_registry.yaml has {len(projects)} projects aligned with repos.yaml",
        )


def check_repo_context_index(state: GateState, root: Path) -> None:
    live = root / "repo_context_index.yaml"
    example = root / "governance" / "repo_context_index.example.yaml"
    if not live.exists():
        state.add("repo_context_index", BLOCKED, "repo_context_index.yaml missing at repo root")
        return
    if not example.exists():
        state.add("repo_context_index", BLOCKED, "governance/repo_context_index.example.yaml missing")
        return
    try:
        from validate_repo_context_index import (
            read_repo_context_index,
            summarize_repo_context_index,
            validate_repo_context_index,
        )
    except ImportError:
        state.add("repo_context_index", BLOCKED, "validate_repo_context_index module unavailable")
        return
    try:
        data = read_repo_context_index(live)
    except ValueError as exc:
        state.add("repo_context_index", BLOCKED, str(exc))
        return
    errors = validate_repo_context_index(data, live.name)
    if errors:
        state.add("repo_context_index", BLOCKED, f"repo_context_index.yaml invalid: {errors[0]}")
        return
    summary = summarize_repo_context_index(data)
    state.add(
        "repo_context_index",
        PASS,
        f"repo_context_index.yaml valid for {summary.get('project_id')} ({summary.get('key_files_count')} key files)",
    )


def check_execpolicy(state: GateState, root: Path) -> None:
    execpolicy_dir = root / "governance" / "execpolicy"
    if not execpolicy_dir.is_dir():
        state.add("execpolicy", BLOCKED, "governance/execpolicy/ missing")
        return
    try:
        from validate_execpolicy import summarize_execpolicy, validate_execpolicy_dir
        from validate_execpolicy import read_execpolicy_file as load_execpolicy_file
    except ImportError:
        state.add("execpolicy", BLOCKED, "validate_execpolicy module unavailable")
        return
    errors = validate_execpolicy_dir(execpolicy_dir)
    if errors:
        state.add("execpolicy", BLOCKED, f"execpolicy invalid: {errors[0]}")
        return
    rules, _ = load_execpolicy_file(execpolicy_dir / "portfolio.rules")
    summary = summarize_execpolicy(rules)
    state.add(
        "execpolicy",
        PASS,
        f"execpolicy rules valid ({summary['total_rules']} portfolio rules, 3 profiles)",
    )


def check_review_queue(state: GateState, root: Path) -> None:
    path = root / "governance" / "review_queue.yaml"
    example = root / "governance" / "review_queue.example.yaml"
    if not path.exists():
        state.add("review_queue", BLOCKED, "governance/review_queue.yaml missing")
        return
    if not example.exists():
        state.add("review_queue", BLOCKED, "governance/review_queue.example.yaml missing")
        return
    try:
        from validate_review_queue import read_review_queue, summarize_review_queue, validate_review_queue
    except ImportError:
        state.add("review_queue", BLOCKED, "validate_review_queue module unavailable")
        return
    try:
        queue = read_review_queue(path)
    except ValueError as exc:
        state.add("review_queue", BLOCKED, str(exc))
        return
    errors = validate_review_queue(queue, path.name)
    if errors:
        state.add("review_queue", BLOCKED, f"review_queue.yaml invalid: {errors[0]}")
        return
    summary = summarize_review_queue(queue)
    state.add(
        "review_queue",
        PASS,
        f"review_queue.yaml valid with {summary['open_items']} open item(s)",
    )


def check_agent_run_example(state: GateState, root: Path) -> None:
    path = root / "governance" / "runs" / "example_run.jsonl"
    template = root / "governance" / "runs" / "agent_run_event.template.json"
    if not path.exists():
        state.add("agent_run_example", BLOCKED, "governance/runs/example_run.jsonl missing")
        return
    if not template.exists():
        state.add("agent_run_example", BLOCKED, "governance/runs/agent_run_event.template.json missing")
        return
    try:
        from validate_agent_run import read_agent_run, validate_agent_run
    except ImportError:
        state.add("agent_run_example", BLOCKED, "validate_agent_run module unavailable")
        return
    errors = validate_agent_run(path)
    if errors:
        state.add("agent_run_example", BLOCKED, f"example_run.jsonl invalid: {errors[0]}")
        return
    events = read_agent_run(path)
    state.add(
        "agent_run_example",
        PASS,
        f"example_run.jsonl valid with {len(events)} event(s)",
    )


def check_proof_of_work_registry(state: GateState, root: Path) -> None:
    path = root / "governance" / "proof_of_work_registry.yaml"
    if not path.exists():
        state.add("proof_of_work_registry", BLOCKED, "governance/proof_of_work_registry.yaml missing")
        return
    data = load_yaml(path)
    records = list(data.get("records", []))
    summary = data.get("summary", {})
    if not records or not summary:
        state.add("proof_of_work_registry", BLOCKED, "proof_of_work_registry.yaml missing records or summary")
        return
    pow_dir = root / "governance" / "proof_of_work"
    json_files = [
        p
        for p in pow_dir.glob("*.json")
        if p.name != "proof_of_work.template.json"
    ] if pow_dir.is_dir() else []
    if len(records) != len(json_files):
        state.add(
            "proof_of_work_registry",
            WARNING,
            f"registry has {len(records)} records but {len(json_files)} proof JSON file(s)",
        )
    else:
        state.add(
            "proof_of_work_registry",
            PASS,
            f"proof_of_work_registry.yaml lists {len(records)} record(s)",
        )


def check_governance_task_queue(state: GateState, root: Path) -> None:
    path = root / "governance" / "governance_task_queue.yaml"
    if not path.exists():
        state.add("governance_task_queue", BLOCKED, "governance/governance_task_queue.yaml missing")
        return
    data = load_yaml(path)
    tasks = list(data.get("tasks", []))
    summary = data.get("summary", {})
    if not tasks or not summary:
        state.add("governance_task_queue", BLOCKED, "governance_task_queue.yaml missing tasks or summary")
        return
    specs_dir = root / "governance" / "task_specs"
    spec_files = [p for p in specs_dir.glob("*.yaml") if p.name != "task_spec.template.yaml"] if specs_dir.is_dir() else []
    if len(tasks) != len(spec_files):
        state.add(
            "governance_task_queue",
            WARNING,
            f"queue has {len(tasks)} tasks but {len(spec_files)} task_spec file(s)",
        )
    else:
        state.add(
            "governance_task_queue",
            PASS,
            f"governance_task_queue.yaml lists {len(tasks)} task(s)",
        )


def check_portfolio_state(state: GateState, root: Path) -> None:
    path = root / "governance" / "portfolio_state.yaml"
    if not path.exists():
        state.add("portfolio_state", BLOCKED, "governance/portfolio_state.yaml missing")
        return
    data = load_yaml(path)
    projects = list(data.get("projects", []))
    summary = data.get("summary", {})
    if not projects or not summary:
        state.add("portfolio_state", BLOCKED, "portfolio_state.yaml missing projects or summary")
        return
    registry = load_yaml(root / "governance" / "project_registry.yaml")
    reg_count = len(registry.get("projects", []))
    if len(projects) != reg_count:
        state.add(
            "portfolio_state",
            WARNING,
            f"portfolio has {len(projects)} projects, registry has {reg_count}",
        )
    else:
        state.add(
            "portfolio_state",
            PASS,
            f"portfolio_state.yaml snapshot covers {len(projects)} projects",
        )


def check_governance_assets(state: GateState, root: Path) -> None:
    required = [
        "governance/project_registry.yaml",
        "governance/project_registry.example.yaml",
        "governance/portfolio_state.yaml",
        "governance/portfolio_state.example.yaml",
        "governance/governance_task_queue.yaml",
        "governance/governance_task_queue.example.yaml",
        "governance/proof_of_work_registry.yaml",
        "governance/proof_of_work_registry.example.yaml",
        "governance/task_specs/example_task_spec.yaml",
        "governance/proof_of_work/example_proof_of_work.json",
        "governance/runs/.gitkeep",
        "governance/runs/agent_run_event.template.json",
        "governance/runs/example_run.jsonl",
        "governance/handoffs/handoff_packet.template.yaml",
        "governance/handoffs/example_handoff_packet.yaml",
        "governance/handoffs/tracking.yaml",
        "governance/checkpoints/.gitkeep",
        "governance/checkpoints/manifest.yaml",
        "docs/checkpoint_snapshot_design.md",
        "config/checkpoint_snapshot_policy.yaml",
        "governance/checkpoint_snapshot_policy.example.yaml",
        "governance/playbook_candidates.yaml",
        "docs/playbook_extraction_design.md",
        "config/playbook_extraction_policy.yaml",
        "governance/playbook_extraction_policy.example.yaml",
        "governance/project_rule_promotion_queue.yaml",
        "docs/project_rule_promotion_design.md",
        "config/project_rule_promotion_policy.yaml",
        "governance/project_rule_promotion_policy.example.yaml",
        "config/protocol_sync_policy.yaml",
        "governance/protocol_sync_policy.example.yaml",
        "governance/protocol_sync_suggestions.yaml",
        "docs/protocol_sync_design.md",
        "config/budget_tracking_policy.yaml",
        "governance/budget_tracking_policy.example.yaml",
        "governance/budget_cost_tracking.yaml",
        "docs/budget_cost_tracking_design.md",
        "config/wip_limit_policy.yaml",
        "governance/wip_limit_policy.example.yaml",
        "governance/wip_limit_status.yaml",
        "docs/wip_limit_scheduling_design.md",
        "config/feishu_notification_policy.yaml",
        "governance/feishu_notification_policy.example.yaml",
        "governance/feishu_notification_plan.yaml",
        "docs/feishu_lark_notification_design.md",
        "config/mac_notification_policy.yaml",
        "governance/mac_notification_policy.example.yaml",
        "docs/mac_local_notification_design.md",
        "governance/execpolicy/profiles/readonly_managed_repo.rules",
        "governance/execpolicy/profiles/repo_ops_guarded.rules",
        "governance/execpolicy/profiles/risky_confirm.rules",
        "docs/data_models.md",
        "docs/reference_architecture_absorption.md",
        "docs/audit_trail_design.md",
        "docs/handoff_protocol.md",
        "docs/review_queue_design.md",
        "docs/execpolicy_design.md",
        "docs/repo_context_index_design.md",
        "docs/scan_policy_design.md",
        "docs/analyzer_policy_design.md",
        "docs/priority_scoring_design.md",
        "docs/lifecycle_policy_design.md",
        "docs/blocker_policy_design.md",
        "docs/evaluation_gate_design.md",
        "docs/failure_recovery_design.md",
        "config/failure_recovery_policy.yaml",
        "governance/failure_recovery_policy.example.yaml",
    ]
    missing = [item for item in required if not (root / item).exists()]
    if missing:
        state.add("governance_assets", BLOCKED, f"missing governance assets: {missing}")
    else:
        state.add("governance_assets", PASS, "governance assets and design docs exist")


def check_task_spec_template(state: GateState, root: Path) -> None:
    path = root / "governance" / "task_specs" / "task_spec.template.yaml"
    if not path.exists():
        state.add("task_spec_template", BLOCKED, "task_spec.template.yaml missing")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "task_id",
        "project_id",
        "working_directory",
        "assigned_agent",
        "acceptance_criteria",
        "validation_commands",
        "execpolicy_profile",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        state.add("task_spec_template", BLOCKED, f"task_spec template missing fields: {missing}")
    else:
        state.add("task_spec_template", PASS, "task_spec template contains required fields")


def check_proof_of_work_template(state: GateState, root: Path) -> None:
    path = root / "governance" / "proof_of_work" / "proof_of_work.template.json"
    if not path.exists():
        state.add("proof_of_work_template", BLOCKED, "proof_of_work.template.json missing")
        return
    text = path.read_text(encoding="utf-8")
    required = [
        "task_id",
        "project_id",
        "changed_files",
        "validation_commands",
        "tests_passed",
        "audit_run_path",
        "known_issues",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        state.add("proof_of_work_template", BLOCKED, f"proof_of_work template missing fields: {missing}")
    else:
        state.add("proof_of_work_template", PASS, "proof_of_work template contains required fields")


def check_eval_registry(state: GateState, root: Path) -> None:
    path = root / "governance" / "evals" / "registry.yaml"
    registry = load_yaml(path)
    eval_ids = {item.get("eval_id") for item in registry.get("evals", [])}
    required = {
        "repo_protocol_exists",
        "agents_md_exists",
        "no_secret_exposure",
        "managed_repo_readonly",
        "dashboard_html_exists",
        "round_state_updated",
        "completion_report_exists",
        "task_spec_schema_valid",
        "proof_of_work_schema_valid",
        "playwright_dashboard_check",
        "eval_registry_runner_valid",
    }
    missing = sorted(required - eval_ids)
    runner = registry.get("runner", {})
    if missing:
        state.add("eval_registry", BLOCKED, f"eval registry missing evals: {missing}")
    elif not isinstance(runner, dict) or not runner.get("script"):
        state.add("eval_registry", BLOCKED, "eval registry missing runner.script")
    else:
        state.add("eval_registry", PASS, "eval registry contains required baseline evals")


def check_handoff_protocol(state: GateState, root: Path) -> None:
    template = root / "governance" / "handoffs" / "handoff_packet.template.yaml"
    example = root / "governance" / "handoffs" / "example_handoff_packet.yaml"
    tracking = root / "governance" / "handoffs" / "tracking.yaml"
    gen_script = root / "scripts" / "generate_handoff_packet.py"
    val_script = root / "scripts" / "validate_handoff_packet.py"
    if not all(p.exists() for p in (template, example, tracking, gen_script, val_script)):
        state.add("handoff_protocol", WARNING, "handoff template/example/tracking or scripts missing")
        return
    try:
        from validate_handoff_packet import validate_handoff_file

        errors = validate_handoff_file(example)
    except Exception as exc:  # noqa: BLE001
        state.add("handoff_protocol", BLOCKED, f"handoff validation import failed: {exc}")
        return
    if errors:
        state.add("handoff_protocol", BLOCKED, f"example handoff invalid: {errors[:3]}")
    else:
        state.add("handoff_protocol", PASS, "handoff_packet generation and tracking wired")


def check_eval_registry_runner(state: GateState, root: Path) -> None:
    script = root / "scripts" / "run_eval_registry.py"
    registry = root / "governance" / "evals" / "registry.yaml"
    if not script.exists() or not registry.exists():
        state.add("eval_registry_runner", WARNING, "run_eval_registry.py or registry.yaml missing")
        return
    text = script.read_text(encoding="utf-8")
    if "run_registry" in text and "DEFAULT_REGISTRY" in text:
        state.add("eval_registry_runner", PASS, "eval registry runner wired (dry-run default)")
    else:
        state.add("eval_registry_runner", WARNING, "eval registry runner incomplete")


def check_completion_report(state: GateState, root: Path) -> None:
    current = load_yaml(root / "round_state" / "current_round.yaml")
    round_name = str(current.get("current_round", ""))
    prefix_match = re.match(r"round_\d+", round_name)
    report_name = f"reports/{prefix_match.group(0)}_completion_report.md" if prefix_match else ""
    path = root / report_name if report_name else Path()
    if path.exists():
        state.add("completion_report", PASS, f"{path.name} exists")
    else:
        state.add("completion_report", WARNING, f"missing completion report for current round: {report_name or 'unknown'}")


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


def render_report(state: GateState) -> str:
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
    return "\n".join(lines) + "\n"


def write_report(state: GateState, root: Path) -> Path:
    report_path = root / "reports" / "agent_gate_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(state), encoding="utf-8")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic gate checks")
    parser.add_argument("--root", default=".", help="Repository root path")
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="persist reports/agent_gate_report.md (requires separate write authority)",
    )
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
    check_ui_check_http(state, root)
    check_audit_report(state, root)
    check_playwright_local_only(state, root)
    check_scan_allowlist_compliance(state, root)
    check_scan_policy(state, root)
    check_analyzer_policy(state, root)
    check_priority_scoring_policy(state, root)
    check_lifecycle_policy(state, root)
    check_blocker_policy(state, root)
    check_wip_limit_policy(state, root)
    check_feishu_notification_policy(state, root)
    check_mac_notification_policy(state, root)
    check_budget_tracking_policy(state, root)
    check_protocol_sync_policy(state, root)
    check_project_rule_promotion_policy(state, root)
    check_playbook_extraction_policy(state, root)
    check_checkpoint_snapshot_policy(state, root)
    check_failure_recovery_policy(state, root)
    check_ui_check_policy(state, root)
    check_cursor_task_spec_prompt(state, root)
    check_codex_task_spec_prompt(state, root)
    check_openclaw_orchestration_bridge(state, root)
    check_weekly_digest(state, root)
    check_daily_briefing(state, root)
    check_openclaw_daily_briefing_skill(state, root)
    check_handoff_protocol(state, root)
    check_handoff_trial(state, root)
    check_governance_hardening(state, root)
    check_backup_restore(state, root)
    check_personal_os_integration(state, root)
    check_protocol_governance_api_ban(state, root)
    check_protocol_version(state, root)
    check_governance_assets(state, root)
    check_project_registry(state, root)
    check_portfolio_state(state, root)
    check_governance_task_queue(state, root)
    check_task_spec_template(state, root)
    check_proof_of_work_template(state, root)
    check_proof_of_work_registry(state, root)
    check_agent_run_example(state, root)
    check_review_queue(state, root)
    check_execpolicy(state, root)
    check_repo_context_index(state, root)
    check_eval_registry(state, root)
    check_eval_registry_runner(state, root)
    check_completion_report(state, root)
    check_requirements_dev_playwright(state, root)
    check_installation_doc(state, root)
    check_example_fixtures(state, root)
    check_pytest_tests(state, root)
    report = write_report(state, root) if args.write_report else None

    print(
        f"[gate] verdict={state.verdict} "
        f"report={report if report is not None else 'not-written'}"
    )
    for item in state.findings:
        print(f"[{item.severity}] {item.check}: {item.message}")
    return EXIT_CODES[state.verdict]


if __name__ == "__main__":
    raise SystemExit(main())
