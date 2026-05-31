# 通知计划

## 稳定契约（任何渠道消费）

见 [`downstream_integrations.md`](downstream_integrations.md)：`repo_status.json`、日报、Feishu 预览 JSON、生成的 Prompt。

## 目标渠道

| 渠道 | 状态 | 说明 |
|------|------|------|
| Markdown 日报/周报 | 已实现 | `generate_report.py` |
| Dashboard | 已实现 | 本地 `file://` |
| Feishu 机器人 | 已实现（opt-in） | `prepare_feishu_payload.py --send` + 环境变量 |
| Mac 本地通知 | 规划 | 可由 Automations / launchd 包装 |
| Telegram | 规划 | 不在本仓库 Round 范围 |
| OpenClaw | 可选适配器 | Skill + 只读脚本 |
| Hermes | 可选适配器 | 消费同一 JSON/报告路径 |
| Cursor Automations | 可选适配器 | 定时跑流水线 + `--send` |
| 本地推理服务 | 可选适配器 | 读 status + 日报生成建议 |

## 原则

- 不把 Webhook / Token 写入仓库
- 默认预览；真实发送需 Human 配置环境变量后显式 `--send`
