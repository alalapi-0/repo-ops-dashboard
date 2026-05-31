# Round 07 - OpenClaw Bridge

## 目标

- 将 OpenClaw 作为调度入口
- 读取 Dashboard 状态
- 触发扫描脚本
- 生成提醒
- 不让 OpenClaw 直接修改业务仓库

## 不做什么

- 不做主力代码开发
- 不做业务仓自动提交

## 输入文件

- `data/repo_status.json`
- `reports/*.md`
- `skills/openclaw_repo_ops/SKILL.md`

## 输出文件

- OpenClaw 调度入口配置文档与脚本

## 具体阶段

1. 只读桥接定义
2. 调度动作最小化
3. 边界验证

## 验收标准

- OpenClaw 仅执行调度/提醒职责

## 风险

- 越权调用需强约束

## 推荐执行 Agent

- Cursor
