# Protocol Sync Suggestions

- generated_at: 2026-06-02T05:20:25.848420+00:00
- reference_protocol_version: 0.3.0
- **只读建议**：不在此脚本中写入任何被管理仓库。

## 各仓差异

| 仓库 | 状态 | 缺失治理文件 |
|------|------|--------------|
| light_novel | active | AGENTS.md, repo_protocol_standard.yaml |
| ai-manga | active | README.md, AGENTS.md, repo_protocol_standard.yaml, CHANGELOG.md, docs/index.md |
| novel-continuation-agent | active | repo_protocol_standard.yaml, CHANGELOG.md |
| repo-ops-dashboard | bootstrap | — |
| old_demo_placeholder | missing | （跳过：路径不可用） |

## 建议执行顺序

1. 高优先级且缺失 `AGENTS.md` / `repo_protocol_standard.yaml` 的 active 仓库
2. 仅有 README/CHANGELOG 缺失的中优先级仓库
3. archived / missing 路径 — Human 决策是否保留登记

## 生成的 Cursor Prompt

见 `prompts/generated/<repo>_protocol_sync.md`（需 `--no-dry-run` 写入）。
