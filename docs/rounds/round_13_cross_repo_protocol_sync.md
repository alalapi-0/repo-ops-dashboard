# Round 13 - Cross-Repo Protocol Sync

## 目标

- 帮助多个仓库同步通用协议（AGENTS.md、repo_protocol_standard.yaml 等）
- **只生成同步建议**，不自动修改业务仓库
- 由 Cursor/Codex 在具体仓库中执行

## 不做什么

- 不批量写入被管理仓库
- 不强制统一所有字段
- 不读取业务源码

## 前置条件

- 多个仓库已在 repos.yaml 登记
- 本仓库 protocol 为参考标准

## 输入文件

- `repo_protocol_standard.yaml`
- `data/repo_snapshots.json`（各仓管理文件快照）

## 输出文件

- `reports/protocol_sync_suggestions.md`
- `prompts/generated/<repo>_protocol_sync.md`

## 阶段任务

### 阶段 1 — 差异检测

- 对比各仓 AGENTS.md / protocol 是否存在及版本
- 列出 missing 与 outdated

### 阶段 2 — 建议生成

- 每仓一份同步建议 Markdown
- 含可复制给 Cursor 的补丁说明（非自动应用）

### 阶段 3 — Human 审批

- 报告汇总需同步的仓库优先级
- Human 选择哪些仓执行

## 验收标准

- 报告列出各仓协议差异
- 无自动 write 到被管理 path
- 生成的 Prompt 边界清晰

## 风险点

- 各仓协议版本 intentionally 不同
- 误建议覆盖定制内容

## 推荐执行 Agent

- Cursor（生成建议）/ Codex（在具体仓执行）

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
实现 protocol 差异报告，输出 reports/protocol_sync_suggestions.md。
禁止自动修改业务仓；为每个需同步仓生成 Cursor Prompt。
```
