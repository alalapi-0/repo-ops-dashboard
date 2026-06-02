#!/usr/bin/env python3
"""Multi-agent handoff trial — OpenClaw read state -> Cursor prompt -> proof_of_work draft (dry-run)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

DEFAULT_TASK_SPEC = "governance/task_specs/example_handoff_trial_task_spec.yaml"
DEFAULT_REPORT = "reports/handoff_trial_report.md"
DEFAULT_POW_DRAFT = "reports/handoff_trial_pow_draft.json"
DEFAULT_POLICY = "governance/handoffs/handoff_trial_policy.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else {}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def build_pow_draft(*, task_spec: dict[str, Any], handoff_id: str, cursor_prompt_path: str) -> dict[str, Any]:
    task_id = str(task_spec.get("task_id", "unknown"))
    return {
        "task_id": task_id,
        "project_id": str(task_spec.get("project_id", "")),
        "status": "draft",
        "completed_at": "",
        "agent_type": "Cursor",
        "working_directory": str(task_spec.get("working_directory", "")),
        "artifacts": list(task_spec.get("artifacts_expected") or []),
        "changed_files": [],
        "validation_commands": list(task_spec.get("validation_commands") or ["python3 scripts/agent_gate.py"]),
        "tests_passed": False,
        "eval_report_path": "",
        "audit_run_path": "",
        "summary": f"Handoff trial draft for {handoff_id}; Cursor prompt at {cursor_prompt_path}",
        "known_issues": ["dry-run trial — not executed"],
        "handoff_id": handoff_id,
        "trial_mode": True,
        "external_api_called": False,
    }


def render_report(
    *,
    round_state: dict[str, Any],
    snapshot: dict[str, Any],
    handoff_id: str,
    cursor_prompt_chars: int,
    pow_draft: dict[str, Any],
    dry_run: bool,
) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""# Handoff Trial Report (Dry-Run)

生成时间：{generated_at}

## 当前轮次

- round：`{round_state.get('current_round', '—')}`
- status：`{round_state.get('status', '—')}`

## 流程步骤

1. **OpenClaw 读状态** — snapshot role={snapshot.get('role', '—')} repos={snapshot.get('repo_count', '—')}
2. **Handoff packet** — id=`{handoff_id}`（dry-run 不写入 tracking）
3. **Cursor Prompt** — {cursor_prompt_chars} chars（dry-run 预览）
4. **proof_of_work 草案** — status=`{pow_draft.get('status')}` trial_mode={pow_draft.get('trial_mode')}

## 安全边界

- dry_run={dry_run}
- external_api_called=False
- managed_repos_write_allowed=False

## HITL

本 trial 需 HumanOwner 审阅后再执行真实 handoff。

---
边界：不读 `.env`、不改被管理业务仓库、不自动 commit/push。
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-agent handoff trial (dry-run default)")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--task-spec", default=DEFAULT_TASK_SPEC)
    parser.add_argument("--status", default="data/repo_status.example.json")
    parser.add_argument("--round-state", default="round_state/current_round.yaml")
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--pow-draft", default=DEFAULT_POW_DRAFT)
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--write", action="store_true", help="Write report and pow draft")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    sys.path.insert(0, str(root / "scripts"))

    import generate_cursor_prompt_from_task_spec as cursor_gen  # noqa: E402
    import generate_handoff_packet as handoff_gen  # noqa: E402
    import openclaw_daily_briefing_skill as openclaw_skill  # noqa: E402

    policy = load_yaml(root / args.policy)
    if policy.get("enabled") is False:
        print("[handoff_trial] disabled by policy")
        return 0

    status = load_json(root / args.status)
    round_state = load_yaml(root / args.round_state)
    spec_path = root / args.task_spec
    if not spec_path.exists():
        raise SystemExit(f"task_spec not found: {spec_path}")

    spec = handoff_gen.load_yaml(spec_path)
    snapshot = openclaw_skill.build_snapshot(
        status=status,
        round_state=round_state,
        review_queue=load_yaml(root / "governance/review_queue.yaml"),
        manifest=load_yaml(root / "governance/openclaw_orchestration.manifest.yaml"),
        reminder="handoff trial",
        digest_paths={"repo_status": str(args.status)},
    )

    packet = handoff_gen.build_packet(spec, repo_root=root)
    handoff_id = str(packet["handoff_id"])

    template_path = root / "prompts/cursor_from_task_spec.md"
    template = cursor_gen.load_template(template_path) if template_path.exists() else ""
    cursor_content = cursor_gen.render_task_spec(template, spec) if template else cursor_gen.build_fallback(spec)

    pow_draft = build_pow_draft(
        task_spec=spec,
        handoff_id=handoff_id,
        cursor_prompt_path=f"prompts/generated/{spec.get('task_id')}_cursor.md",
    )

    dry_run = args.dry_run and not args.write
    report = render_report(
        round_state=round_state,
        snapshot=snapshot,
        handoff_id=handoff_id,
        cursor_prompt_chars=len(cursor_content),
        pow_draft=pow_draft,
        dry_run=dry_run,
    )

    print(
        f"[handoff_trial] handoff={handoff_id} prompt_chars={len(cursor_content)} "
        f"repos={snapshot.get('repo_count')} dry_run={dry_run}"
    )

    if dry_run:
        print("[dry-run] report and pow draft not written")
        return 0

    report_path = root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"[ok] report -> {report_path}")

    pow_path = root / args.pow_draft
    pow_path.parent.mkdir(parents=True, exist_ok=True)
    pow_path.write_text(json.dumps(pow_draft, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[ok] pow draft -> {pow_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
