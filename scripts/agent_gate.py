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
        "governance/checkpoints/.gitkeep",
        "governance/execpolicy/profiles/readonly_managed_repo.rules",
        "governance/execpolicy/profiles/repo_ops_write.rules",
        "governance/execpolicy/profiles/risky_confirm.rules",
        "docs/data_models.md",
        "docs/reference_architecture_absorption.md",
        "docs/audit_trail_design.md",
        "docs/handoff_protocol.md",
        "docs/review_queue_design.md",
        "docs/execpolicy_design.md",
        "docs/repo_context_index_design.md",
        "docs/evaluation_gate_design.md",
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
    }
    missing = sorted(required - eval_ids)
    if missing:
        state.add("eval_registry", BLOCKED, f"eval registry missing evals: {missing}")
    else:
        state.add("eval_registry", PASS, "eval registry contains required baseline evals")


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
    check_eval_registry(state, root)
    check_completion_report(state, root)
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
