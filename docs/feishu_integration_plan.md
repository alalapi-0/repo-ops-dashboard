# Feishu/Lark 接入规划

Round 08：**仅本地预览**，不自动推送、不存 Token。

## 已实现

- `scripts/prepare_feishu_payload.py` — 从日报生成 `reports/feishu_payload_preview.json`
- 路径脱敏（仅保留仓库名与摘要）
- `--send` 需 `FEISHU_WEBHOOK_URL` 环境变量，且本轮**不实现 HTTP 发送**（Human 复制预览或后续轮次）

## 人工确认流程

1. 运行 `python3 scripts/generate_report.py`
2. 运行 `python3 scripts/prepare_feishu_payload.py`
3. 打开 `reports/feishu_payload_preview.json` Review
4. Human 决定是否粘贴到 Feishu 机器人/表格

## 安全原则

- 不上传敏感路径或密钥
- Webhook URL 仅通过环境变量，禁止入库
- 默认 mock/dry-run，真实发送需 Human opt-in
