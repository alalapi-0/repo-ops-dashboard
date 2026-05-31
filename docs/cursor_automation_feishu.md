# Cursor Automations × 飞书定时推送（Round 16）

> **扩展阅读**：主编排与 LLM opt-in 见 [`cursor_automation_guide.md`](cursor_automation_guide.md)。

本仓库不内置 Cursor Automations 配置；在 Cursor 产品 UI 中创建定时任务，执行本仓库脚本即可。

## 前置条件

1. 已完成 [`feishu_integration_plan.md`](feishu_integration_plan.md) 中的飞书群机器人配置。
2. 本机 `.env` 或 Automation Secrets 中配置（**禁止提交 git**）：
   - `FEISHU_WEBHOOK_URL`
   - 可选 `FEISHU_SIGN_SECRET`
3. 真实仓库登记在 [`config/repos.yaml`](../config/repos.yaml)（勿仅用 example）。

## 推荐 Automation 配置

| 项 | 建议值 |
|----|--------|
| **名称** | Repo Ops 每日飞书推送 |
| **Trigger** | Cron，工作日 09:05，`Asia/Shanghai`（错开飞书整点限流） |
| **工作目录** | 本仓库根目录（含 `scripts/refresh_status.sh`） |
| **命令** | 见下方 |

### 仅群推送（Round 16）

```bash
./scripts/refresh_status.sh --feishu-send
```

### 群推送 + 多维表格同步（Round 17 启用后）

```bash
./scripts/refresh_status.sh --feishu-send --bitable-sync
```

也可分两条 Automation：一条 `--feishu-send`，一条在 refresh 之后单独跑 Bitable（见 [`feishu_bitable_schema.md`](feishu_bitable_schema.md)）。

## Secrets / 环境变量

在 Cursor Automation 的 Secrets 或本机 `.env` 中注入：

| 变量 | 用途 | 轮次 |
|------|------|------|
| `FEISHU_WEBHOOK_URL` | 群机器人 Webhook | 16 |
| `FEISHU_SIGN_SECRET` | 机器人签名校验（可选） | 16 |
| `FEISHU_APP_ID` | 开放平台应用 | 17 |
| `FEISHU_APP_SECRET` | 开放平台应用 | 17 |
| `FEISHU_BITABLE_APP_TOKEN` | 多维表格 app_token | 17 |
| `FEISHU_BITABLE_TABLE_ID` | 数据表 table_id | 17 |

若 Automation 运行环境无法 source `.env`，请用包装脚本：

```bash
./scripts/feishu_send.sh --send   # 仅补发飞书（需已生成日报）
```

## 试跑与验收

1. **不发送，只验证流水线**：

```bash
./scripts/refresh_status.sh --example
```

2. **本地预览飞书卡片**：

```bash
python3 scripts/prepare_feishu_payload.py --status data/repo_status.example.json
cat reports/feishu_payload_preview.json
```

3. **手动发送一次**（确认群能收到）：

```bash
./scripts/feishu_send.sh --send
# 或
./scripts/refresh_status.sh --feishu-send
```

4. **Automation 首次启用**：建议先去掉 `--feishu-send` 跑通 refresh，再加发送开关。

## 失败策略

- Automation 日志中查看 exit code；`prepare_feishu_payload.py --send` 失败时 exit 2。
- 本地始终保留 `reports/feishu_payload_preview.json` 与 `reports/daily_repo_report.md`，可人工 `./scripts/feishu_send.sh --send` 补发。
- 不打印 Webhook URL 或 App Secret。

## 相关文档

- 飞书机器人：[`feishu_integration_plan.md`](feishu_integration_plan.md)
- 多维表格：[`feishu_bitable_schema.md`](feishu_bitable_schema.md)
- 调度总览：[`scheduler.md`](scheduler.md)
- 下游集成：[`downstream_integrations.md`](downstream_integrations.md)
