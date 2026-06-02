#!/usr/bin/env python3
"""Compute retry/failure_class/checkpoint/review_queue actions (dry-run, no external API)."""

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

DEFAULT_POLICY = "config/failure_recovery_policy.yaml"
DEFAULT_REPORT = "reports/failure_recovery_plan.md"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


def load_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return load_yaml(path)


def failure_class_index(policy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(entry.get("id", "")): entry
        for entry in policy.get("failure_classes", [])
        if isinstance(entry, dict) and entry.get("id")
    }


def pick_escalation(policy: dict[str, Any], retry_count: int) -> dict[str, Any]:
    levels = list(policy.get("review_queue_escalation", {}).get("levels", []))
    chosen = levels[0] if levels else {"level": "log", "action": "log_only", "after_retry_count": 0}
    for entry in levels:
        if not isinstance(entry, dict):
            continue
        if retry_count >= int(entry.get("after_retry_count", 0)):
            chosen = entry
    return {
        "level": str(chosen.get("level", "log")),
        "action": str(chosen.get("action", "log_only")),
        "after_retry_count": int(chosen.get("after_retry_count", 0)),
    }


def plan_recovery(
    *,
    task_id: str,
    failure_class: str,
    retry_count: int,
    policy: dict[str, Any],
) -> dict[str, Any]:
    classes = failure_class_index(policy)
    meta = dict(classes.get(failure_class, classes.get(str(policy.get("defaults", {}).get("failure_class", "transient")), {})))
    max_retry = int(policy.get("retry", {}).get("max_retry_count", 3))
    retry_eligible = bool(meta.get("retry_eligible", True))
    can_retry = retry_eligible and retry_count < max_retry
    escalation = pick_escalation(policy, retry_count)
    checkpoint_required = bool(policy.get("checkpoint", {}).get("required_on_failure", True))
    prefix = str(policy.get("checkpoint", {}).get("id_prefix", "ckpt_"))
    checkpoint_id = f"{prefix}{task_id}_r{retry_count}" if checkpoint_required else None

    next_retry_count = retry_count + 1 if can_retry else retry_count
    action = "retry" if can_retry else "stop"
    if not can_retry and escalation["action"] == "create_review_queue_item":
        action = "escalate_review_queue"
    if not can_retry and escalation["action"] == "require_human_owner_decision":
        action = "require_hitl"

    return {
        "task_id": task_id,
        "failure_class": failure_class,
        "retry_count": retry_count,
        "next_retry_count": next_retry_count,
        "max_retry_count": max_retry,
        "retry_eligible": retry_eligible,
        "can_retry": can_retry,
        "action": action,
        "checkpoint_id": checkpoint_id,
        "escalation": escalation,
        "auto_approve": bool(policy.get("retry", {}).get("auto_approve", True)),
        "dry_run": True,
    }


def render_report(plan: dict[str, Any]) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    esc = plan.get("escalation", {})
    return "\n".join(
        [
            "# Failure Recovery Plan",
            "",
            f"- generated_at: {ts}",
            f"- task_id: {plan.get('task_id')}",
            f"- failure_class: {plan.get('failure_class')}",
            f"- retry_count: {plan.get('retry_count')} / {plan.get('max_retry_count')}",
            f"- action: {plan.get('action')}",
            f"- checkpoint_id: {plan.get('checkpoint_id')}",
            f"- escalation: {esc.get('level')} → {esc.get('action')}",
            f"- dry_run: {plan.get('dry_run')}",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan failure recovery (dry-run)")
    parser.add_argument("--task-id", default="task_example")
    parser.add_argument("--failure-class", default="transient")
    parser.add_argument("--retry-count", type=int, default=0)
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--output", default=DEFAULT_REPORT)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    policy_path = root / args.policy
    policy = load_policy(policy_path)

    from validate_failure_recovery_policy import validate_failure_recovery_policy

    errors = validate_failure_recovery_policy(policy, source=policy_path.name)
    if errors:
        print(f"[failure_recovery] policy invalid: {errors[:5]}")
        return 2

    plan = plan_recovery(
        task_id=args.task_id,
        failure_class=args.failure_class,
        retry_count=args.retry_count,
        policy=policy,
    )
    report_path = root / args.output
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(plan), encoding="utf-8")

    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(
            f"[failure_recovery] action={plan['action']} checkpoint={plan.get('checkpoint_id')} "
            f"escalation={plan['escalation']['action']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
