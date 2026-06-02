# Daily Briefing Template (Governance MVP)

生成时间：2026-06-02 17:51 UTC

## 当前轮次

- round：`round_56_feishu_lark_notification_mvp`
- status：`completed`
- next：`round_57_mac_local_notification`

## 今日最该推进（1–3 仓）

1. **repo-ops-dashboard**（Cursor）— 处理扫描 warning 并补齐可选治理文件；卡点：无卡点
2. **novel-continuation-agent**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：repo_protocol_standard.yaml missing
3. **light_novel**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：AGENTS.md missing; repo_protocol_standard.yaml missing

## 今日暂缓 / 不该碰

- **ai-manga**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：README.md missing; AGENTS.md missing; repo_protocol_standard.yaml missing
- **old_demo_placeholder**（Human）— 确认仓库路径是否有效，或从登记中归档；卡点：repository path missing

## 待 HumanOwner 决策

- **rq_001_personal_agent_os_positioning**：是否将 repo-ops-dashboard 定位升级为 Personal Agent OS / Portfolio Orchestrator？
- **rq_002_openclaw_orchestration**：是否允许后续接 OpenClaw 调度入口？
- **rq_003_feishu_daily_report**：是否允许后续接 Feishu 日报？
- **rq_004_weekly_priority_ranking**：是否允许后续生成每周优先级排序？
- **rq_005_project_frozen_candidate**：是否允许某项目进入 frozen 状态？

## 风险提醒

- 有卡点仓库 4 个：light_novel, ai-manga, novel-continuation-agent, old_demo_placeholder
- 归档候选：old_demo_placeholder

## 给 Cursor/Codex 的执行草案

- **repo-ops-dashboard** → Cursor：无
- **novel-continuation-agent** → Human：repo_protocol_standard.yaml missing
- **light_novel** → Human：AGENTS.md missing; repo_protocol_standard.yaml missing

## 建议触发命令（默认 dry-run / 只读）

```bash
python3 scripts/agent_gate.py
python3 scripts/refresh_status.sh --example
python3 scripts/openclaw_orchestration_bridge.py --dry-run
```

## 短提醒（≤200 字）

Round round_56_feishu_lark_notification_mvp：今日优先 repo-ops-dashboard, novel-continuation-agent。暂缓 2 仓；review_queue 待决 5 项。编程交给 Cursor/Codex，决策留给 HumanOwner。

---

边界：不读 `.env`、不改被管理业务仓库、不自动 commit/push。
