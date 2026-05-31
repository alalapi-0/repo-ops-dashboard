# 个人操作系统远期路线图

> repo-ops-dashboard 定位为**多仓库治理中枢**，不替代 Cursor/Codex 编程，不自动修改业务仓。

## 愿景

将分散在多个 Git 仓库、文档、日程与 AI 工具中的「个人项目状态」聚合为可读的每日/每周决策面，由 OpenClaw 编排提醒，Human 做最终优先级与归档决策。

## 模块划分

| 模块 | 角色 | 与 repo-ops 关系 |
|------|------|------------------|
| **项目（Repos）** | 核心 | 本仓库：扫描、分析、Dashboard、Prompt |
| **日程** | 独立工具 / 日历只读 | repo-ops 仅链接「今日时间块」，不存详细日程 |
| **学习** | 笔记仓 / 独立 repo | 登记为 `type: learning`，priority 复盘纳入 |
| **工作** | 收入相关 repo | `priority_factors` 中 type 代理相关性 |
| **财务投入** | 独立表格（本地） | 不接入 API；周报 Human 填写 |
| **AI 额度** | 厂商控制台手动 | 简报中 Human 备注，不自动拉取 |
| **周报复盘** | priority_review + OpenClaw brief | 已有脚本扩展 |

## 边界

- **只读聚合**：repo-ops 不写入被管理业务仓、不读 `.env`、不全盘扫源码。
- **独立工具**：日程/记账/额度追踪若需深度功能，单独小工具或 SaaS，经 Markdown/JSON 导出供 repo-ops 引用。
- **OpenClaw**：跨模块提醒入口（读 brief + 日报），不主力写代码。

## 分期路线图

### Phase A — 仓库中枢稳定（Round 00–14，已完成）

- 扫描 → 分析 → Dashboard → 报告 → Feishu 预览 → Playwright → pytest → OpenClaw brief
- 验收：`./scripts/refresh_status.sh --example --ui-check` PASS

### Phase B — 复盘与协议（Round 12–13，已完成）

- priority_review、protocol_sync 建议
- Human 在 `repos.yaml` 覆盖 priority_hint

### Phase C — 轻量扩展（Round 18 部分完成）

- ✅ 周报模板合并：`scripts/generate_weekly_review.py` → `reports/weekly_review.md`
- ✅ Dashboard「本周 Human 笔记」：`data/human_notes.example.json` + 只读展示
- ⏳ 可选只读导入：日历 ICS 路径、本地 CSV 财务摘要（Round 19 完成，见 `read_local_imports.py`）

### Phase D — 个人 OS 外壳（远期）

- 统一入口页（静态 HTML 或 Obsidian/Notion 链接集）
- OpenClaw 每日 9:00：gate → refresh → brief → 可选 Feishu `--send`（Human 启用；见 [`cursor_automation_feishu.md`](cursor_automation_feishu.md)）

## Agent 分工（保持不变）

| Agent | 职责 |
|-------|------|
| Cursor | 本仓库实现、UI、文档 |
| Codex | 边界清楚的批量推进（业务仓） |
| OpenClaw | 读 status/report/brief，编排 Prompt |
| Human | 优先级、冻结、归档、通知、财务/日程真实数据 |

## 验收（Round 15）

- 本文档结构完整，明确 repo-ops 不膨胀为「全能 OS 实现」
- 无强制实现代码；后续 Phase C/D 逐项 Human 授权后再开 Round
