# Round 16 - Cursor Automations Feishu Push

## 目标

- `refresh_status.sh` 增加 `--feishu-send` opt-in 开关
- 增强飞书卡片：概览统计、OpenClaw 摘要
- 文档说明 Cursor Automations 定时执行 refresh + 发送

## 不做什么

- 不在仓库内保存 Automation 配置或 Webhook Token
- 不默认自动 `--send`
- 不接入 Cursor Cloud Agent Webhooks

## 前置条件

- Round 08 `prepare_feishu_payload.py` 可用
- Human 配置飞书群机器人 Webhook

## 输入文件

- `data/repo_status.json`
- `reports/daily_repo_report.md`
- `reports/openclaw_daily_brief.md`

## 输出文件

- `docs/cursor_automation_feishu.md`
- 更新的 `scripts/refresh_status.sh`、`scripts/prepare_feishu_payload.py`

## 验收标准

- `./scripts/refresh_status.sh --example` PASS
- `--feishu-send` 仅在 env 齐全时发送
- 卡片含概览 / 高优 / OpenClaw 摘要
- `agent_gate.py` PASS

## 推荐执行 Agent

- Cursor（脚本与文档）/ Human（Automation 与 Token）

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
实现 refresh_status.sh --feishu-send 与增强 prepare_feishu_payload.py。
编写 docs/cursor_automation_feishu.md。禁止 Token 入库。
```
