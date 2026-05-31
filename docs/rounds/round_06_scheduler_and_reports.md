# Round 06 - Scheduler and Reports

## 目标

- 生成日报/周报 Markdown
- 支持本周建议汇总
- 记录最近更新时间
- **先不接**外部通知

## 不做什么

- 不接 Feishu/Telegram/Mac 通知
- 不自动 cron 部署（仅提供脚本）
- 不调用外部 API

## 前置条件

- `data/repo_status.json` 存在
- `scripts/generate_report.py` 基础版存在

## 输入文件

- `data/repo_status.json`

## 输出文件

- `reports/daily_repo_report.md`
- `reports/weekly_repo_report.md`

## 阶段任务

### 阶段 1 — 日报结构

- 高优先级、卡点、freeze/archive 分区
- Cursor/Codex 任务列表

### 阶段 2 — 周报增强

- 本周变化对比（如有历史快照）
- 建议推进/暂停列表

### 阶段 3 — 调度文档

- 文档说明如何用 cron/launchd 本地调度
- 默认 dry-run 预览

## 验收标准

- 日报/周报可生成且可读
- 含 generated_at 时间戳
- 无外部通知 SDK

## 风险点

- 无历史数据时周报对比有限
- 本地 cron 需用户自行配置

## 推荐执行 Agent

- Cursor / Codex

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
完善 generate_report.py 日报/周报格式。
验证：python3 scripts/generate_report.py --input data/repo_status.example.json --output reports/daily_repo_report.md
```
