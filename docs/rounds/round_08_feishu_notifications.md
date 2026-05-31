# Round 08 - Feishu Notifications

## 目标

- 规划飞书机器人或飞书表格推送
- 推送日报/周报摘要
- 所有通知内容**先本地生成，再人工确认**
- 不上传密钥、不上传敏感路径

## 不做什么

- 不在仓库中存储 Webhook Token
- 不自动推送（需 Human 确认）
- 不上传完整 repo 路径列表到公网

## 前置条件

- `reports/daily_repo_report.md` 可稳定生成
- 用户有 Feishu 机器人或表格（Human 提供）

## 输入文件

- `reports/daily_repo_report.md`
- `reports/weekly_repo_report.md`
- `docs/feishu_integration_plan.md`

## 输出文件

- `scripts/prepare_feishu_payload.py`（仅生成本地 JSON/Markdown，不发送）
- 更新的 `docs/feishu_integration_plan.md`

## 阶段任务

### 阶段 1 — 载荷格式

- 定义 Feishu 消息 JSON 结构（无密钥）
- 脱敏路径（仅仓库名）

### 阶段 2 — 本地预览脚本

- 生成 `reports/feishu_payload_preview.json`
- 默认不调用 API

### 阶段 3 — 人工确认流程

- 文档说明 Human 如何复制到 Feishu
- 或 `--send` 需显式 env 且不在 git 中

## 验收标准

- 无 Token 入库
- 预览载荷可读
- 发送需显式 opt-in

## 风险点

- 误提交 Webhook URL
- 消息含敏感路径

## 推荐执行 Agent

- Cursor（脚本）/ Human（Token 与发送）

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
实现 prepare_feishu_payload.py，从日报生成本地预览 JSON。
禁止硬编码 Token。发送必须 --send + 环境变量，且 .env 不入库。
```
