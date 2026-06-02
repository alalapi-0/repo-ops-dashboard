#!/usr/bin/env python3
"""Run baseline evals registered in governance/evals/registry.yaml (no external API)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

DEFAULT_REGISTRY = "governance/evals/registry.yaml"
DEFAULT_REPORT = "reports/eval_registry_run.md"

SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}"),
    re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH|PRIVATE) KEY-----"),
)

TASK_SPEC_REQUIRED = (
    "task_id",
    "project_id",
    "working_directory",
    "assigned_agent",
    "acceptance_criteria",
    "validation_commands",
    "execpolicy_profile",
)

POW_TEMPLATE_REQUIRED = (
    "task_id",
    "project_id",
    "changed_files",
    "validation_commands",
    "tests_passed",
    "audit_run_path",
    "known_issues",
)


@dataclass(frozen=True)
class EvalOutcome:
    eval_id: str
    status: str
    message: str
    required: bool


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else {}


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


def resolve_completion_report(root: Path) -> Path | None:
    current = load_yaml(root / "round_state" / "current_round.yaml")
    round_name = str(current.get("current_round", ""))
    match = re.match(r"round_\d+", round_name)
    if not match:
        return None
    path = root / "reports" / f"{match.group(0)}_completion_report.md"
    return path if path.exists() else None


def check_secret_patterns(root: Path) -> list[str]:
    candidates = run_git_lines(["git", "ls-files"], root)
    hits: list[str] = []
    for rel in candidates:
        if rel.startswith(".env") and rel != ".env.example":
            hits.append(rel)
            continue
        path = root / rel
        if not path.is_file() or path.stat().st_size > 200_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                hits.append(rel)
                break
    return hits


def check_managed_repo_readonly(root: Path) -> list[str]:
    cfg = load_yaml(root / "config" / "managed_files.yaml")
    denylist = cfg.get("denylist", [])
    if not denylist:
        return ["config/managed_files.yaml denylist is empty"]
    allowlist = cfg.get("allowlist", [])
    overlap = [item for item in allowlist if any(token in item.lower() for token in ["env", "token", "secret"])]
    if overlap:
        return [f"suspicious allowlist entries: {overlap}"]
    return []


def check_round_state(root: Path, rel_path: str) -> list[str]:
    data = load_yaml(root / rel_path)
    missing = [key for key in ("current_round", "status", "next_round") if not str(data.get(key, "")).strip()]
    return [f"missing round_state fields: {missing}"] if missing else []


def run_schema_eval(root: Path, eval_id: str, rel_path: str) -> list[str]:
    path = root / rel_path
    if not path.exists():
        return [f"missing file: {rel_path}"]

    if eval_id == "execpolicy_valid":
        from validate_execpolicy import validate_execpolicy_dir

        return validate_execpolicy_dir(path.parent if path.name.endswith(".rules") else path.parent)

    if eval_id == "review_queue_valid":
        from validate_review_queue import read_review_queue, validate_review_queue

        return validate_review_queue(read_review_queue(path))

    if eval_id == "repo_context_index_valid":
        from validate_repo_context_index import read_repo_context_index, validate_repo_context_index

        return validate_repo_context_index(read_repo_context_index(path))

    if eval_id == "agent_run_jsonl_valid":
        from validate_agent_run import validate_agent_run

        return validate_agent_run(path)

    policy_loaders: dict[str, tuple[str, str]] = {
        "scan_policy_valid": ("validate_scan_policy", "validate_scan_policy"),
        "analyzer_policy_valid": ("validate_analyzer_policy", "validate_analyzer_policy"),
        "priority_scoring_policy_valid": (
            "validate_priority_scoring_policy",
            "validate_priority_scoring_policy",
        ),
        "lifecycle_policy_valid": ("validate_lifecycle_policy", "validate_lifecycle_policy"),
        "blocker_policy_valid": ("validate_blocker_policy", "validate_blocker_policy"),
        "ui_check_policy_valid": ("validate_ui_check_policy", "validate_ui_check_policy"),
    }
    if eval_id in policy_loaders:
        module_name, fn_name = policy_loaders[eval_id]
        mod = __import__(module_name)
        fn = getattr(mod, fn_name)
        return fn(load_yaml(path))

    if eval_id == "task_spec_schema_valid":
        text = path.read_text(encoding="utf-8")
        return [f"missing field: {f}" for f in TASK_SPEC_REQUIRED if f not in text]

    if eval_id == "proof_of_work_schema_valid":
        text = path.read_text(encoding="utf-8")
        return [f"missing field: {f}" for f in POW_TEMPLATE_REQUIRED if f not in text]

    if eval_id == "handoff_packet_valid":
        from validate_handoff_packet import read_handoff_packet, validate_handoff_packet

        return validate_handoff_packet(read_handoff_packet(path), source=path.name)

    if eval_id == "handoff_tracking_valid":
        data = load_yaml(path)
        items = data.get("items", [])
        if not isinstance(items, list) or not items:
            return ["tracking.items empty"]
        for item in items:
            if not isinstance(item, dict):
                return ["tracking item must be mapping"]
            if not str(item.get("handoff_id", "")).startswith("handoff_"):
                return ["handoff_id prefix invalid"]
        return []

    if eval_id == "eval_registry_runner_valid":
        reg = load_yaml(path)
        runner = reg.get("runner", {})
        if not isinstance(runner, dict) or not runner.get("script"):
            return ["registry.runner.script missing"]
        script = root / str(runner["script"])
        if not script.exists():
            return [f"runner script missing: {runner['script']}"]
        return []

    return []


def run_single_eval(
    root: Path,
    entry: dict[str, Any],
    *,
    dry_run: bool,
    skip_ui: bool,
) -> EvalOutcome:
    eval_id = str(entry.get("eval_id", "unknown"))
    required = bool(entry.get("required", True))
    eval_type = str(entry.get("type", ""))
    rel_path = str(entry.get("path", "")).strip()

    try:
        if eval_type == "file_exists":
            if eval_id == "completion_report_exists":
                report = resolve_completion_report(root)
                if report is None:
                    raise ValueError("completion report for current round not found")
            else:
                target = root / rel_path
                if not target.exists():
                    raise FileNotFoundError(rel_path)
        elif eval_type == "static_scan":
            hits = check_secret_patterns(root)
            if hits:
                raise ValueError(f"possible secrets in: {hits[:5]}")
        elif eval_type == "policy_check":
            errors = check_managed_repo_readonly(root)
            if errors:
                raise ValueError("; ".join(errors))
        elif eval_type == "yaml_check":
            errors = check_round_state(root, rel_path)
            if errors:
                raise ValueError("; ".join(errors))
        elif eval_type == "schema_check":
            errors = run_schema_eval(root, eval_id, rel_path)
            if errors:
                raise ValueError("; ".join(errors[:8]))
        elif eval_type == "ui_check":
            if dry_run or skip_ui:
                return EvalOutcome(eval_id, "SKIP", "ui_check skipped (dry-run)", required)
            cmd = str(entry.get("command", "")).strip()
            if not cmd:
                raise ValueError("ui_check missing command")
            parts = cmd.split()
            completed = subprocess.run(parts, cwd=str(root), check=False, capture_output=True, text=True)
            if completed.returncode != 0:
                raise RuntimeError(f"ui_check exit {completed.returncode}")
        else:
            raise ValueError(f"unsupported eval type: {eval_type}")
        return EvalOutcome(eval_id, "PASS", "ok", required)
    except Exception as exc:  # noqa: BLE001 — eval runner aggregates failures
        return EvalOutcome(eval_id, "FAIL", str(exc), required)


def load_registry(path: Path) -> list[dict[str, Any]]:
    data = load_yaml(path)
    evals = data.get("evals", [])
    if not isinstance(evals, list):
        return []
    return [item for item in evals if isinstance(item, dict)]


def run_registry(
    root: Path,
    registry_path: Path,
    *,
    dry_run: bool = True,
    skip_ui: bool = True,
    required_only: bool = False,
) -> list[EvalOutcome]:
    entries = load_registry(registry_path)
    outcomes: list[EvalOutcome] = []
    for entry in entries:
        if required_only and not entry.get("required", True):
            continue
        outcomes.append(run_single_eval(root, entry, dry_run=dry_run, skip_ui=skip_ui))
    return outcomes


def summarize(outcomes: list[EvalOutcome]) -> dict[str, Any]:
    failed_required = [o for o in outcomes if o.required and o.status == "FAIL"]
    skipped = [o for o in outcomes if o.status == "SKIP"]
    passed = [o for o in outcomes if o.status == "PASS"]
    failed_optional = [o for o in outcomes if not o.required and o.status == "FAIL"]
    verdict = "BLOCKED" if failed_required else ("WARNING" if failed_optional else "PASS")
    return {
        "verdict": verdict,
        "passed": len(passed),
        "failed_required": len(failed_required),
        "failed_optional": len(failed_optional),
        "skipped": len(skipped),
        "total": len(outcomes),
    }


def render_report(outcomes: list[EvalOutcome], summary: dict[str, Any]) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Eval Registry Run",
        "",
        f"- generated_at: {ts}",
        f"- verdict: {summary['verdict']}",
        f"- passed: {summary['passed']}/{summary['total']}",
        f"- failed_required: {summary['failed_required']}",
        f"- skipped: {summary['skipped']}",
        "",
        "## Results",
    ]
    for item in outcomes:
        lines.append(f"- [{item.status}] `{item.eval_id}` ({'required' if item.required else 'optional'}): {item.message}")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run eval registry baseline checks")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY, help="Registry YAML path")
    parser.add_argument("--output", default=DEFAULT_REPORT, help="Markdown report path")
    parser.add_argument(
        "--run-ui-check",
        action="store_true",
        help="Execute playwright ui_check eval (default: skip ui_check)",
    )
    parser.add_argument("--required-only", action="store_true", help="Only run required evals")
    parser.add_argument("--json", action="store_true", help="Print JSON summary to stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    registry_path = root / args.registry
    if not registry_path.exists():
        print(f"[eval] registry missing: {registry_path}")
        return 2

    outcomes = run_registry(
        root,
        registry_path,
        dry_run=not args.run_ui_check,
        skip_ui=not args.run_ui_check,
        required_only=args.required_only,
    )
    summary = summarize(outcomes)
    report_text = render_report(outcomes, summary)
    output_path = root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_text, encoding="utf-8")

    if args.json:
        payload = {
            "verdict": summary["verdict"],
            "outcomes": [
                {
                    "eval_id": o.eval_id,
                    "status": o.status,
                    "message": o.message,
                    "required": o.required,
                }
                for o in outcomes
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"[eval] verdict={summary['verdict']} report={output_path}")

    exit_codes = {"PASS": 0, "WARNING": 1, "BLOCKED": 2}
    return exit_codes.get(str(summary["verdict"]), 2)


if __name__ == "__main__":
    raise SystemExit(main())
