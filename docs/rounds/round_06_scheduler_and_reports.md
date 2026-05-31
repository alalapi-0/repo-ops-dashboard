# Round 06 - Scheduler and Reports

## 目标

- 生成日报/周报
- 支持最近更新时间
- 支持本周推荐推进项目
- 暂不接外部通知

## 不做什么

- 不接真实通知 API

## 输入文件

- `data/repo_status.json`

## 输出文件

- `reports/daily_repo_report.md`
- `reports/weekly_repo_report.md`

## 具体阶段

1. 报告模板完善
2. 时间与统计补全
3. 调度入口预留

## 验收标准

- 报告可读、字段完整、可复用

## 风险

- 统计规则需要持续校准

## 推荐执行 Agent

- Cursor / Codex
