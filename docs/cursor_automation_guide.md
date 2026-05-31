# Cursor Automations × Repo Ops 调度指南

本仓库不内置 Cursor Automations 配置；在 Cursor 产品 UI 或本地 CLI Agent 中创建定时任务，执行本仓库脚本即可。

> 飞书专项说明仍见 [`cursor_automation_feishu.md`](cursor_automation_feishu.md)（Round 16 原文档，本节为其超集）。

## 主编排路径（替代 OpenClaw）

| 方式 | 适合 | 命令 |
|------|------|------|
| **Cursor Automations** | 已用 Cursor、要定时 refresh + 可选推送 | `./scripts/refresh_status.sh [--feishu-send] [--llm-summary] [--call]` |
| **本地 cron / launchd** | 不依赖 Cursor 云 | 同上 |
| **Cursor CLI Agent** | 本地 Cursor CLI 调度 | 在工作目录执行同一 refresh 命令 |

OpenClaw Skill 已标记为**可选遗留**；新部署请使用本指南。

## 前置条件

1. 真实仓库登记在 [`config/repos.yaml`](../config/repos.yaml)
2. 复制 [`../.env.example`](../.env.example) → `.env`（见 [`env_configuration.md`](env_configuration.md)）
3. 首次建议：`./scripts/refresh_status.sh --example --ui-check`

## 推荐 Automation 配置

| 项 | 建议值 |
|----|--------|
| **名称** | Repo Ops 每日刷新 |
| **Trigger** | Cron `5 9 * * 1-5`（工作日 09:05，**错开飞书整点限流**） |
| **时区** | `Asia/Shanghai` |
| **工作目录** | 本仓库根目录 |
| **命令** | 见下方 |

### 标准 refresh（不调用外部 API）

```bash
./scripts/refresh_status.sh
```

### refresh + 飞书推送

```bash
./scripts/refresh_status.sh --feishu-send
```

### refresh + LLM 摘要（OpenRouter opt-in）

```bash
# .env: LLM_ENABLED=true, OPENROUTER_API_KEY=...
./scripts/refresh_status.sh --llm-summary --call
```

### 全量（LLM + 飞书 + Bitable）

```bash
./scripts/refresh_status.sh --llm-summary --call --feishu-send --bitable-sync
```

## Secrets / 环境变量

| 变量 | 用途 |
|------|------|
| `OPENROUTER_API_KEY` | LLM `--call` |
| `LLM_ENABLED` | 必须为 `true` 才允许 `--call` |
| `FEISHU_WEBHOOK_URL` | 群机器人 |
| `FEISHU_SIGN_SECRET` | 签名校验（可选） |
| `FEISHU_APP_*` / `FEISHU_BITABLE_*` | Bitable 同步 |

完整映射见 [`env_configuration.md`](env_configuration.md)。

## 试跑与验收

```bash
./scripts/refresh_status.sh --example
python3 scripts/generate_llm_summary.py   # dry-run
python3 scripts/prepare_feishu_payload.py --status data/repo_status.example.json
open dashboard/hub.html
```

## 失败策略

- 查看 Automation 日志 exit code
- 本地产物：`reports/daily_repo_report.md`、`reports/feishu_payload_preview.json` 可人工补发
- 飞书错误码提示见 [`feishu_integration_plan.md`](feishu_integration_plan.md)
- 不打印 Webhook URL 或 API Key

## 相关文档

- 个人 OS 路线：[`personal_os_roadmap.md`](personal_os_roadmap.md)
- 下游集成：[`downstream_integrations.md`](downstream_integrations.md)
- 调度总览：[`scheduler.md`](scheduler.md)
