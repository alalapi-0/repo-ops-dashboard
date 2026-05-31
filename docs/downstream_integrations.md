# 下游集成（多路线，不绑定单一调度器）

`repo-ops-dashboard` 产出**稳定文件契约**；调度与推送由你任选下游实现。

## 稳定契约（只读这些即可）

| 产物 | 路径 | 用途 |
|------|------|------|
| 状态 JSON | `data/repo_status.json` | 优先级、blocker、lifecycle、归档候选 |
| 快照 JSON | `data/repo_snapshots.json` | 扫描原始结果 |
| 日报 | `reports/daily_repo_report.md` | 人类阅读 |
| 规则简报 | `reports/daily_brief.md` | 每日决策（规则） |
| LLM 摘要 | `reports/llm_daily_summary.md` | OpenRouter opt-in |
| 周报 | `reports/weekly_repo_report.md` | 可选 |
| Feishu 载荷 | `reports/feishu_payload_preview.json` | 机器人推送 |
| Bitable 同步 | `scripts/sync_feishu_bitable.py` | 多维表格 upsert |
| Prompt | `prompts/generated/*.md` | Cursor/Codex 执行 |
| Dashboard | `dashboard/index.html` | 本地浏览 |
| Hub | `dashboard/hub.html` | 统一入口 |

## 推荐本地流水线

```bash
cd /path/to/repo-ops-dashboard
./scripts/refresh_status.sh
# 或带 opt-in：
./scripts/refresh_status.sh --llm-summary --call --feishu-send
```

## 路线对比（任选，可并存）

| 路线 | 适合 | 接法 |
|------|------|------|
| **Cursor Automations** | 已用 Cursor、要定时推送 | [`cursor_automation_guide.md`](cursor_automation_guide.md) |
| **本地 cron / launchd** | 不依赖 Cursor 云 | 同上 refresh 命令 |
| **OpenClaw** | 遗留 Skill 用户 | [`skills/openclaw_repo_ops/SKILL.md`](../skills/openclaw_repo_ops/SKILL.md)（deprecated） |
| **Hermes** | 另有任务中枢 | 轮询 `repo_status.json` / 日报 |

## 设计原则

- 本仓库**不**实现第三方 SDK 入库；Feishu / OpenRouter 使用 stdlib HTTP。
- 扫描脚本**不读** `.env`；opt-in 脚本在 `--send` / `--call` 时读取环境变量。

## 相关文档

- 环境变量：[`env_configuration.md`](env_configuration.md)
- Feishu：[`feishu_integration_plan.md`](feishu_integration_plan.md)
- 通知：[`notification_plan.md`](notification_plan.md)
