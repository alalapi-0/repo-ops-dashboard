# OpenClaw 集成规划

OpenClaw 在 Personal Agent OS 中只作为调度入口和提醒入口，不作为主力编程 Agent。

## OpenClaw 未来只做

- 读取 `portfolio_state`
- 读取 `weekly_digest`
- 读取 `review_queue`
- 读取 `data/repo_status.json`
- 触发只读扫描脚本
- 生成今日建议
- 生成 Cursor/Codex Prompt
- 提醒用户处理 HITL 决策
- 可接 Feishu/Telegram/Mac 通知，但只能发送低敏摘要，且需 HumanOwner 授权

## OpenClaw 不做

- 主力编程开发
- 自动修改业务仓库
- 自动删除项目
- 自动提交或推送
- 自动发布
- 全仓库扫描
- 读取密钥、`.env`、token、私钥
- 绕过 review_queue 决策

## 推荐接入阶段

- Round 25：仅规划，不连接真实 OpenClaw。
- Round 43：规划 OpenClaw orchestration bridge。
- Round 58：低风险多 Agent handoff trial。

## Skill

`skills/openclaw_repo_ops/SKILL.md` 是 OpenClaw 使用说明，必须与本文件和 `repo_protocol_standard.yaml` 保持一致。
