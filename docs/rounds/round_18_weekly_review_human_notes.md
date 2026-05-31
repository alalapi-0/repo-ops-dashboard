# Round 18 - Weekly Review Merge & Human Notes Dashboard

## 目标

- 合并 priority_review + openclaw brief + weekly report 为统一周报复盘
- Dashboard 展示「本周 Human 笔记」（手动 JSON，无 API）
- 纳入 refresh 链路与 Playwright 检查

## 不做什么

- 不接入日历/财务 API
- 不自动修改 human_notes（Human 手编辑 JSON）
- 不扩大扫描范围

## 前置条件

- Round 12–14 脚本可用
- Playwright 已安装

## 输入文件

- `reports/priority_review.md`（或 example 变体）
- `reports/openclaw_daily_brief.md`
- `reports/weekly_repo_report.md`
- `data/human_notes.json`（可选，gitignore）

## 输出文件

- `reports/weekly_review.md`
- `data/human_notes.example.json`
- Dashboard human-notes 区块

## 阶段任务

### 阶段 1 — 周报合并

- `scripts/generate_weekly_review.py` 拼接四段内容

### 阶段 2 — Human 笔记

- example JSON + Dashboard 只读展示

### 阶段 3 — 集成

- refresh_status.sh、ui_check、pytest

## 验收标准

- `generate_weekly_review.py` 可生成 weekly_review.md
- Dashboard 含 `.human-notes` 区块（有 example 数据时）
- agent_gate / pytest / ui_check PASS

## 风险点

- human_notes 与 status 不同步（预期：Human 维护）

## 推荐执行 Agent

- Cursor

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
实现 generate_weekly_review.py 与 Dashboard human notes 区块。
合并 priority_review + openclaw brief + weekly report；Human 笔记来自 JSON。
```
