# Round 14 - OpenClaw Daily Briefing

> **已迁移（Round 21）**：实现已重命名为 `generate_daily_brief.py` / `reports/daily_brief.md`；编排主线改为 Cursor Automations。

## 目标

- 让 OpenClaw 每天读取报告，生成每日简报
- 今日最该推进的 1–3 个仓库
- 今日不该碰的仓库
- 卡住原因与建议交给 Cursor/Codex 的任务
- 简短提醒语

## 不做什么

- 不让 OpenClaw 写代码或改仓库
- 不自动发送通知（除非 Human 启用 Round 08）
- 不调用外部 LLM API（使用规则模板）

## 前置条件

- Round 07 OpenClaw Bridge 文档/Skill 就绪
- 日报/ status 可每日更新

## 输入文件

- `data/repo_status.json`
- `reports/daily_repo_report.md`

## 输出文件

- `reports/openclaw_daily_brief.md`
- `prompts/openclaw_daily_brief.md`（模板）

## 阶段任务

### 阶段 1 — 规则选题

- 按 priority + blockers 选 top 3 推进仓
- 选 freeze/archived/low health 为「不该碰」

### 阶段 2 — 简报生成

- `scripts/generate_openclaw_brief.py` 或 Skill 步骤
- 输出 Markdown 简报

### 阶段 3 — OpenClaw 集成

- Skill 增加「每日 9:00 读 brief」流程（文档级）
- 提醒语 ≤ 200 字

## 验收标准

- 简报含推进/暂停/任务/提醒四段
- OpenClaw 仅读+生成文本
- 无业务仓写入

## 风险点

- 规则选题不符合 Human 意图
- 需 Human 微调 priority

## 推荐执行 Agent

- Cursor（脚本）/ OpenClaw（读取执行）/ Human（复核）

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
生成 reports/openclaw_daily_brief.md：top3 推进、不该碰、卡点、Cursor/Codex 任务、短提醒。
OpenClaw 只读 status/report，不编程。
```
