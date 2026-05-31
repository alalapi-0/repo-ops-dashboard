# Round 05 - Prompt Generator

## 目标

- 根据每个仓库状态生成下一轮 Prompt
- 区分 Cursor Prompt、Codex Prompt、OpenClaw 调度 Prompt
- **不自动执行** Prompt

## 不做什么

- 不自动调用 Cursor/Codex API
- 不自动提交代码
- 不修改被管理仓库

## 前置条件

- `data/repo_status.json` 存在
- `prompts/` 模板目录存在

## 输入文件

- `data/repo_status.json`
- `prompts/cursor_next_round.md`
- `prompts/codex_next_round.md`
- `prompts/openclaw_repo_scan.md`

## 输出文件

- `prompts/generated/<repo>_cursor.md`
- `prompts/generated/<repo>_codex.md`
- `prompts/generated/<repo>_openclaw.md`

## 阶段任务

### 阶段 1 — 模板引擎

- 读取 status 字段填充模板变量
- 支持 blockers、next_actions 注入

### 阶段 2 — 分 Agent 生成

- Cursor：本地开发/UI/脚本
- Codex：批量测试/PR
- OpenClaw：只读扫描触发/提醒文本

### 阶段 3 — 输出与校验

- 写入 `prompts/generated/`
- Human Review 后再执行

## 验收标准

- 每仓可生成 3 类 Prompt 文件
- Prompt 含明确目标与边界
- 无自动执行逻辑

## 风险点

- Prompt 质量依赖 status 准确性
- 需避免泄露路径/密钥

## 推荐执行 Agent

- Cursor / Codex

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
实现 scripts/generate_prompts.py，从 repo_status.json 生成三类 Prompt。
只写 prompts/generated/，不自动执行。
```
