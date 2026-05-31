# Feishu/Lark 接入规划

## 已实现

- `scripts/prepare_feishu_payload.py` — 从日报 + status + OpenClaw brief 生成 `reports/feishu_payload_preview.json`
- 路径脱敏（仅保留仓库名与摘要）
- `--send` — 通过环境变量 `FEISHU_WEBHOOK_URL` 使用 stdlib HTTP POST（opt-in，禁止入库）
- `scripts/refresh_status.sh --feishu-send` — 刷新后 opt-in 发送（见 [`cursor_automation_feishu.md`](cursor_automation_feishu.md)）
- `scripts/sync_feishu_bitable.py` — 多维表格同步（默认 dry-run，`--sync` opt-in，见 [`feishu_bitable_schema.md`](feishu_bitable_schema.md)）

## 你在飞书侧的一次性配置

1. 打开目标群聊 → **设置** → **群机器人** → **添加机器人** → **自定义机器人**。
2. 复制 **Webhook 地址**（形如 `https://open.feishu.cn/open-apis/bot/v2/hook/...`）。
3. 在本机配置 Webhook（**不要提交真实 URL**）：

**方式 A（推荐）**：复制 `.env.example` 为 `.env`，填入 `FEISHU_WEBHOOK_URL`（`.env` 已在 `.gitignore`）。

**方式 B**：在 `~/.zshrc` 中 `export FEISHU_WEBHOOK_URL='...'`。

发送时可使用包装脚本（自动 source `.env`）：

```bash
./scripts/feishu_send.sh --send
```

4. 若机器人启用了 **签名校验**，额外设置：

```bash
export FEISHU_SIGN_SECRET='机器人安全设置中的签名密钥'
```

5. 先跑完整流水线生成日报，再预览、再发送：

```bash
python3 scripts/generate_report.py --input data/repo_status.json --output reports/daily_repo_report.md
python3 scripts/prepare_feishu_payload.py
python3 scripts/prepare_feishu_payload.py --send
```

## 安全原则

- 不上传完整本地路径或密钥
- Webhook URL / Sign Secret 仅环境变量
- 日志不打印完整 Webhook URL
- 默认不 `--send`；定时任务需显式加 `--send`

## 故障排查

| 现象 | 处理 |
|------|------|
| `FEISHU_WEBHOOK_URL not set` | 在当前 shell 或 launchd/Cursor Automation 环境中 export |
| HTTP 403 / 签名校验失败 | 设置 `FEISHU_SIGN_SECRET` 或关闭机器人签名校验后重试 |
| `code` 非 0 | 检查 JSON 卡片格式；用预览文件在飞书调试工具验证 |
| 群收不到消息 | 确认机器人已加入该群、Webhook 未轮换 |

## 与下游集成

推送只是可选出口；详见 [`downstream_integrations.md`](downstream_integrations.md)（Cursor Automations / OpenClaw / Hermes / 本地推理服务均可调用同一脚本）。
