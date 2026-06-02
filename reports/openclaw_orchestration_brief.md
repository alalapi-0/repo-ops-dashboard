# OpenClaw Orchestration Brief

生成时间：2026-06-02 17:54 UTC

## 当前轮次

- round：`round_60_multi_agent_handoff_trial`
- status：`completed`
- next：`round_61_portfolio_governance_hardening`

## Portfolio 摘要

- 项目总数：17
- 活跃：14
- 阻塞：3
- review_queue 待决：5
- budget_warning：False

## 待 HumanOwner 决策（review_queue）

- **rq_001_personal_agent_os_positioning**（positioning_change）：是否将 repo-ops-dashboard 定位升级为 Personal Agent OS / Portfolio Orchestrator？
- **rq_002_openclaw_orchestration**（integration_permission）：是否允许后续接 OpenClaw 调度入口？
- **rq_003_feishu_daily_report**（notification_permission）：是否允许后续接 Feishu 日报？
- **rq_004_weekly_priority_ranking**（governance_policy）：是否允许后续生成每周优先级排序？
- **rq_005_project_frozen_candidate**（lifecycle_decision）：是否允许某项目进入 frozen 状态？

## 活跃治理任务

- **task_handoff_trial_001**（Cursor）— Handoff trial — 验证 OpenClaw 读状态到 Cursor Prompt 到 proof_of_work 草案
- **task_light_novel_governance_prompt_001**（Cursor）— 为 light_novel 仓库生成 README/docs/CHANGELOG 同步治理 Prompt
- **task_repo_ops_test_fix_001**（Codex）— 修复 repo-ops-dashboard 示例测试与 gate 报告

## 今日最该推进（1–3 项目）

1. **ai-anime-short-factory**（Codex）— Run scan_repos.py and refresh status snapshot；卡点：无卡点
2. **ai-manga**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：README.md missing; AGENTS.md missing; repo_protocol_standard.yaml missing
3. **novel-continuation-agent**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：repo_protocol_standard.yaml missing

## 今日暂缓 / 不该碰

- 无

## 建议触发命令（默认 dry-run / 只读）

```bash
python3 scripts/agent_gate.py
python3 scripts/openclaw_daily_briefing_skill.py --dry-run
python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/generate_report.py --input data/repo_status.example.json
python3 scripts/openclaw_orchestration_bridge.py --dry-run
python3 scripts/generate_daily_briefing.py --input data/repo_status.example.json --dry-run
```

## 短提醒（≤200 字）

Round round_60_multi_agent_handoff_trial：优先 ai-anime-short-factory, ai-manga。暂缓 0 项；review_queue 待决 5 项。OpenClaw 只读编排，编程交给 Cursor/Codex。

---

边界：不读 `.env`、不改被管理业务仓库、不自动 commit/push、不调用外部 API。
