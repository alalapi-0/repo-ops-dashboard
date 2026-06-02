# CHANGELOG

## Round 60 - Multi-Agent Handoff Trial

- 新增 `run_handoff_trial.py`（OpenClaw 读状态 → Cursor Prompt → proof_of_work 草案，dry-run 默认）。
- 新增 handoff trial task_spec 与 policy；`refresh_status.sh` 与 `agent_gate` 纳入验收。
- `reports/round_60_completion_report.md`。

## Round 59 - Browser Dashboard Interaction

- 新增 `ui_check_http.sh`（127.0.0.1:8765/dashboard/ HTTP 预览检查）。
- `ui_check.py` 增加 repo 卡片 state 属性检查；`refresh_status.sh` 增加 `--http-ui-check`。
- `reports/round_59_completion_report.md`。

## Round 58 - OpenClaw Daily Briefing Skill

- 新增 `openclaw_daily_briefing_skill.py`（读 repo_status + digest，dry-run 默认）。
- 更新 OpenClaw skill、manifest、`refresh_status.sh` 与 `agent_gate` 验收。
- `reports/round_58_completion_report.md`。

## Round 57 - Mac Local Notification
