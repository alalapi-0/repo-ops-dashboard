# 个人操作系统远期路线图

> repo-ops-dashboard 定位为**多仓库治理中枢**，不替代 Cursor/Codex 编程，不自动修改业务仓。

## 愿景

将分散在多个 Git 仓库、文档、日程与 AI 工具中的「个人项目状态」聚合为可读的每日/每周决策面，由 **Cursor Automations / 本地 CLI** 编排定时 refresh，Human 做最终优先级与归档决策。

## 模块划分

| 模块 | 角色 | 与 repo-ops 关系 |
|------|------|------------------|
| **项目（Repos）** | 核心 | 本仓库：扫描、分析、Dashboard、Prompt |
| **日程** | 独立工具 / 日历只读 | Round 19 ICS 只读摘要 |
| **学习** | 笔记仓 / 独立 repo | 登记为 `type: learning` |
| **工作** | 收入相关 repo | `priority_factors` 中 type 代理相关性 |
| **财务投入** | 本地 CSV | Round 19 只读摘要 |
| **AI 额度** | 厂商控制台手动 | Human 备注，不自动拉取 |
| **LLM 摘要** | OpenRouter opt-in | `generate_llm_summary.py` |
| **周报复盘** | priority_review + daily_brief | `generate_weekly_review.py` |

## 边界

- **只读聚合**：repo-ops 不写入被管理业务仓、扫描脚本不读 `.env`、不全盘扫源码。
- **独立工具**：日程/记账若需深度功能，单独小工具，经 Markdown/JSON 导出供引用。
- **编排**：Cursor Automations / cron 跑 `refresh_status.sh`；OpenClaw 为可选遗留适配器。

## 分期路线图

### Phase A — 仓库中枢稳定（Round 00–14，已完成）

- 扫描 → 分析 → Dashboard → 报告 → Feishu 预览 → Playwright → pytest → daily brief（原 OpenClaw brief）

### Phase B — 复盘与协议（Round 12–13，已完成）

- priority_review、protocol_sync

### Phase C — 轻量扩展（Round 18–19，已完成）

- 周报复盘、Human notes、本地 ICS/CSV 导入

### Phase D — 个人 OS 外壳（Round 20–24，已完成）

| Round | 内容 | 状态 |
|-------|------|------|
| 20 | `.env.example` + OpenRouter 模板 + 配置文档 | ✅ |
| 21 | OpenClaw → daily_brief 重命名；Cursor Automations 主线 | ✅ |
| 22 | OpenRouter LLM 摘要 opt-in | ✅ |
| 23 | 飞书 20KB/错误码/签名单测加固 | ✅ |
| 24 | `dashboard/hub.html` 统一入口 | ✅ |

## Agent 分工

| Agent | 职责 |
|-------|------|
| Cursor | 本仓库实现、UI、文档、Automations 配置 |
| Codex | 边界清楚的批量推进（业务仓） |
| Cursor Automations | 定时 refresh、可选飞书/LLM opt-in |
| OpenClaw | **可选遗留**；读 status/report，不主力编程 |
| Human | 优先级、冻结、归档、密钥、财务/日程真实数据 |

## 日常命令

```bash
./scripts/refresh_status.sh --llm-summary --call --feishu-send
open dashboard/hub.html
```

## 验收

- Phase D 各 Round 有 spec + completion report
- `python3 scripts/agent_gate.py` 与 `pytest` PASS
- 无强制 OpenClaw 依赖
