# OpenClaw Daily Briefing Skill

生成时间：2026-06-02 17:58 UTC

## 当前轮次

- round：`round_63_personal_agent_os_long_term_integration`
- status：`completed`
- next：`maintenance_mode`

## Repo Status 摘要

- 仓库数：5
- 有卡点：4
- 扫描时间：2026-06-02T17:58:19.176418+00:00

## 今日最该推进（1–3 仓）

1. **repo-ops-dashboard**（Cursor）— 处理扫描 warning 并补齐可选治理文件；卡点：无卡点
2. **novel-continuation-agent**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：repo_protocol_standard.yaml missing
3. **light_novel**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：AGENTS.md missing; repo_protocol_standard.yaml missing

## 今日暂缓 / 不该碰

- **ai-manga**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：README.md missing; AGENTS.md missing; repo_protocol_standard.yaml missing
- **old_demo_placeholder**（Human）— 确认仓库路径是否有效，或从登记中归档；卡点：repository path missing

## Daily Briefing 摘要

- # Daily Briefing Template (Governance MVP)
- 生成时间：2026-06-02 17:58 UTC
- ## 当前轮次
- round：`round_63_personal_agent_os_long_term_integration`
- status：`completed`
- next：`maintenance_mode`
- ## 今日最该推进（1–3 仓）
- 1. **repo-ops-dashboard**（Cursor）— 处理扫描 warning 并补齐可选治理文件；卡点：无卡点
- 2. **novel-continuation-agent**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：repo_protocol_standard.yaml missing
- 3. **light_novel**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：AGENTS.md missing; repo_protocol_standard.yaml missing
- ## 今日暂缓 / 不该碰
- **ai-manga**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：README.md missing; AGENTS.md missing; repo_protocol_standard.yaml missing
- … 另有 24 行

## Weekly Digest 摘要

- # Weekly Digest Template
- 生成时间：2026-06-02 17:57 UTC
- ## 本周摘要
- 扫描仓库：5
- 活跃项目：14
- 阻塞项目：3
- 治理轮次：见 round_state
- ## Portfolio 状态
- 项目总数：17
- 活跃：14
- 阻塞：3
- review_queue 待决：5
- … 另有 29 行

## 待 HumanOwner 决策

- **rq_001_personal_agent_os_positioning**：是否将 repo-ops-dashboard 定位升级为 Personal Agent OS / Portfolio Orchestrator？
- **rq_002_openclaw_orchestration**：是否允许后续接 OpenClaw 调度入口？
- **rq_003_feishu_daily_report**：是否允许后续接 Feishu 日报？
- **rq_004_weekly_priority_ranking**：是否允许后续生成每周优先级排序？
- **rq_005_project_frozen_candidate**：是否允许某项目进入 frozen 状态？

## 建议触发命令（默认 dry-run / 只读）

```bash
python3 scripts/agent_gate.py
python3 scripts/openclaw_daily_briefing_skill.py --dry-run
python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/generate_report.py --input data/repo_status.example.json
python3 scripts/openclaw_orchestration_bridge.py --dry-run
python3 scripts/personal_os_integration_snapshot.py --write
python3 scripts/generate_daily_briefing.py --input data/repo_status.example.json --dry-run
```

## 短提醒（≤200 字）

Round round_63_personal_agent_os_long_term_integration：优先 repo-ops-dashboard, novel-continuation-agent。暂缓 2 仓；review_queue 待决 5 项。OpenClaw 只读 digest/repo_status，编程交给 Cursor/Codex。

---

边界：不读 `.env`、不改被管理业务仓库、不自动 commit/push、不调用外部 API。
