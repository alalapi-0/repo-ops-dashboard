# 可选适配器：OpenClaw

OpenClaw 是**可选**下游之一，非唯一调度路线。通用契约见 [`downstream_integrations.md`](downstream_integrations.md)。

## OpenClaw 可做

1. 调度入口（cron 替代或补充）
2. 读取 `data/repo_status.json`
3. 读取 `reports/`
4. 生成今日/本周建议（基于报告，不读业务源码）
5. 触发只读扫描脚本（`scan_repos.py` 等）
6. 生成给 Cursor/Codex 的 Prompt
7. 可选：调用 `prepare_feishu_payload.py --send` 或交给人/Mac 通知

## OpenClaw 不做

1. 主力代码开发
2. 大规模重构
3. 自动删除仓库
4. 自动提交业务仓库
5. 全量读取源码

## Skill

[`skills/openclaw_repo_ops/SKILL.md`](../skills/openclaw_repo_ops/SKILL.md) — 仅在选择 OpenClaw 时启用。
