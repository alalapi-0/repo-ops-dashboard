# Round 05 - Prompt Generator

## 目标

- 按仓库状态自动生成给 Cursor/Codex 的 Prompt
- 每个仓库输出独立任务建议
- 仅生成，不自动执行

## 不做什么

- 不触发自动代码修改

## 输入文件

- `data/repo_status.json`

## 输出文件

- `prompts/cursor_next_round.md`
- `prompts/codex_next_round.md`

## 具体阶段

1. 模板设计
2. 任务分发建议生成
3. 提示词质量校验

## 验收标准

- Prompt 可直接被 Agent 使用

## 风险

- 模板冗长导致执行偏差

## 推荐执行 Agent

- Codex
