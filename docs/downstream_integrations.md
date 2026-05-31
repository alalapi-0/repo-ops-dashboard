# 下游集成（多路线，不绑定单一调度器）

`repo-ops-dashboard` 产出**稳定文件契约**；调度与推送由你任选下游实现。

## 稳定契约（只读这些即可）

| 产物 | 路径 | 用途 |
|------|------|------|
| 状态 JSON | `data/repo_status.json` | 优先级、blocker、lifecycle、归档候选 |
| 快照 JSON | `data/repo_snapshots.json` | 扫描原始结果 |
| 日报 | `reports/daily_repo_report.md` | 人类阅读 |
| 周报 | `reports/weekly_repo_report.md` | 可选 |
| Feishu 载荷 | `reports/feishu_payload_preview.json` | 机器人推送 |
| Bitable 同步 | `scripts/sync_feishu_bitable.py` | 多维表格 upsert（Round 17） |
| Prompt | `prompts/generated/*.md` | Cursor/Codex 执行 |
| Dashboard | `dashboard/index.html` | 本地浏览 |

登记配置：[`config/repos.yaml`](../config/repos.yaml)（真实环境）；示例：[`config/repos.example.yaml`](../config/repos.example.yaml)。

## 推荐本地流水线

```bash
cd /path/to/repo-ops-dashboard
python3 scripts/scan_repos.py --config config/repos.yaml --no-dry-run
python3 scripts/analyze_repos.py
python3 scripts/generate_dashboard.py
python3 scripts/generate_report.py
python3 scripts/generate_prompts.py --no-dry-run
python3 scripts/prepare_feishu_payload.py          # 预览
python3 scripts/prepare_feishu_payload.py --send   # 可选：需 FEISHU_WEBHOOK_URL
python3 scripts/ui_check.py --file dashboard/index.html --headless true
```

## 路线对比（任选，可并存）

| 路线 | 适合 | 接法 |
|------|------|------|
| **Cursor Automations** | 已用 Cursor、要定时推送 | 见 [`cursor_automation_feishu.md`](cursor_automation_feishu.md)；`refresh_status.sh --feishu-send [--bitable-sync]` |
| **OpenClaw** | 已有 OpenClaw 习惯 | 使用 [`skills/openclaw_repo_ops/SKILL.md`](../skills/openclaw_repo_ops/SKILL.md)，读 status + reports，触发只读脚本 |
| **Hermes** | 另有任务/消息中枢 | Hermes 轮询或订阅 `repo_status.json` / 日报路径；本仓库不内置 Hermes 客户端 |
| **本地推理服务** | 自定义摘要/对话 | 定时读 JSON + 日报，模型输出建议写入 `prompts/` 或仅发 Feishu |

## 设计原则

- 本仓库**不**实现第三方 SDK（`lark_oapi` 等）入库；Feishu 发送仅在 `prepare_feishu_payload.py --send` 使用 stdlib。
- **不**自动删除被管理仓库；生命周期见 [`lifecycle_rules.md`](lifecycle_rules.md)。
- 新 PycharmProjects 子目录：[`scripts/sync_repo_registry.py`](../scripts/sync_repo_registry.py) 合并登记，不覆盖已有 `priority_hint`。

## 相关文档

- OpenClaw（可选）：[`openclaw_integration_plan.md`](openclaw_integration_plan.md)
- Feishu：[`feishu_integration_plan.md`](feishu_integration_plan.md)
- 通知渠道列表：[`notification_plan.md`](notification_plan.md)
- 调度：[`scheduler.md`](scheduler.md)
