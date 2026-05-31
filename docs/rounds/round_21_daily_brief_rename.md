# Round 21 - Daily Brief Rename & Cursor Orchestration

## 目标

- 一次性重命名 `openclaw_*` → `daily_brief` / `orchestration`
- 文档主线切换为 Cursor Automations / CLI
- OpenClaw 降为可选遗留

## 不做什么

- 不改变规则简报逻辑
- 不删除 `skills/openclaw_repo_ops/`（加 deprecation 注记）

## 验收标准

- `generate_daily_brief.py` 替代旧脚本
- `refresh_status.sh` 与测试 PASS
- `docs/cursor_automation_guide.md` 存在

## 推荐执行 Agent

- Cursor

## 可复制给 Cursor 的任务摘要

重命名 openclaw 产物；更新 refresh/weekly_review/prompts；写 cursor_automation_guide.md。
