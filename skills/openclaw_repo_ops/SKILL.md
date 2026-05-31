---
name: repo_ops_dashboard
description: Read and summarize repo-ops-dashboard status, generate next actions, and help orchestrate Cursor/Codex work without modifying managed repositories.
---

# OpenClaw Repo Ops Skill

## 何时使用

- 需要汇总 `repo-ops-dashboard` 当前状态
- 需要生成今日/本周推进建议
- 需要产出给 Cursor/Codex 的下一轮 Prompt

## 默认行为

- 默认只读
- 只操作 `repo-ops-dashboard`
- 不直接修改被管理仓库

## 可执行动作

- 运行只读扫描脚本
- 读取 `data/repo_status.json`
- 生成提醒文本
- 生成 Cursor/Codex Prompt
