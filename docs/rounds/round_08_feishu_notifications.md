# Round 08 - Feishu Notifications

## 目标

- 接飞书机器人
- 推送日报/周报
- 可选同步到飞书表格
- 不上传敏感路径或密钥

## 不做什么

- 不绕过密钥治理策略

## 输入文件

- `reports/*.md`
- `docs/feishu_integration_plan.md`

## 输出文件

- Feishu 通知适配层文档与脚本

## 具体阶段

1. 凭据管理策略
2. 消息模板与发送流程
3. 风险审计

## 验收标准

- 具备可控 dry-run 与审计记录

## 风险

- 权限与数据外发风险

## 推荐执行 Agent

- Cursor
