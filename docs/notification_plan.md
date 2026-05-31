# 通知计划

## 稳定契约

见 [`downstream_integrations.md`](downstream_integrations.md)：`repo_status.json`、日报、`daily_brief.md`、LLM 摘要、Feishu 预览 JSON。

## 目标渠道

| 渠道 | 状态 | 说明 |
|------|------|------|
| Markdown 日报/周报 | 已实现 | `generate_report.py` |
| Dashboard / Hub | 已实现 | `dashboard/index.html`、`dashboard/hub.html` |
| Feishu 机器人 | 已实现（opt-in） | `prepare_feishu_payload.py --send` |
| Feishu 多维表格 | 已实现（opt-in） | `sync_feishu_bitable.py --sync` |
| Cursor Automations | 已实现（文档） | [`cursor_automation_guide.md`](cursor_automation_guide.md) |
| OpenRouter LLM | 已实现（opt-in） | `generate_llm_summary.py --call` |
| Mac 本地通知 | 规划 | launchd 包装 refresh |
| OpenClaw | 可选遗留 | Skill deprecated |

## 原则

- 不把 Webhook / Token 写入仓库
- 默认预览；真实发送/LLM 需 Human 配置 `.env` 后显式 opt-in
