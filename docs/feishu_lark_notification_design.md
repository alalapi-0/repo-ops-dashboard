# Feishu/Lark 日报/周报通知规划

## 目标

规划飞书机器人日报/周报推送节奏与内容契约，**默认不接真实 API**；HumanOwner 通过 `review_queue` 批准后再 opt-in 发送。

## 机器可读资产

| 文件 | 说明 |
|------|------|
| `config/feishu_notification_policy.yaml` | 渠道、排期、内容规则、HITL 关联 |
| `governance/feishu_notification_plan.yaml` | 当前规划快照（来源文件就绪状态、建议 cron） |
| `reports/feishu_notification_planning.md` | 人类可读规划报告 |

## 已有脚本（扩展而非重复）

| 脚本 | 角色 |
|------|------|
| `scripts/prepare_feishu_payload.py` | 从日报/简报生成卡片预览 JSON |
| `scripts/plan_feishu_notifications.py` | 本轮：汇总排期与来源就绪状态（无 API） |
| `scripts/send_feishu_notification.py` | Round 56：MVP 发送/出站预览（dry-run 默认） |
| `scripts/feishu_send.sh` | 包装脚本，source `.env` 后 `--send` |

## 排期建议

| 类型 | 建议 cron | 卡片标题 | 主要来源 |
|------|-----------|----------|----------|
| 日报 | `5 9 * * 1-5` | Repo Ops 日报摘要 | daily_report + daily_brief + status |
| 周报 | `10 17 * * 5` | Repo Ops 周报摘要 | weekly_report + weekly_digest + priority_review |

## 内容与安全

- 路径脱敏：仅保留仓库名与摘要（`prepare_feishu_payload.redact_paths`）。
- Webhook / Sign Secret **仅环境变量**，禁止入库。
- 默认 `dry_run: true`；`--send` 需 `FEISHU_WEBHOOK_URL` 且 HITL 项 `rq_003_feishu_daily_report` 已批准。
- 请求体上限 20KB，超限自动截断。

## 验证命令

```bash
python3 scripts/validate_feishu_notification_policy.py
python3 scripts/plan_feishu_notifications.py --write
python3 scripts/prepare_feishu_payload.py
python3 scripts/agent_gate.py
```

## 与下游集成

见 [`feishu_integration_plan.md`](feishu_integration_plan.md)、[`notification_plan.md`](notification_plan.md)、[`downstream_integrations.md`](downstream_integrations.md)。
