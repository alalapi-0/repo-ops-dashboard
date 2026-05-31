# Protocol Sync Suggestions

- generated_at: 2026-05-31T21:58:52.239246+00:00
- reference_protocol_version: 0.2.0
- **只读建议**：不在此脚本中写入任何被管理仓库。

## 各仓差异

| 仓库 | 状态 | 缺失治理文件 |
|------|------|--------------|
| novel-continuation-agent | active | repo_protocol_standard.yaml, CHANGELOG.md |
| ai-manga | empty | （跳过：路径不可用） |
| repo-ops-dashboard | bootstrap | — |
| ai-anime-short-factory | active | repo_protocol_standard.yaml |
| wechat-article-scheduler | active | repo_protocol_standard.yaml, CHANGELOG.md |
| light_novel | active | AGENTS.md, repo_protocol_standard.yaml |
| computer_study_plan | active | repo_protocol_standard.yaml, CHANGELOG.md, docs/index.md |
| world-news-lens | active | repo_protocol_standard.yaml |
| pixel-world-asset-forge | active | AGENTS.md, repo_protocol_standard.yaml, docs/index.md |
| agent-experiments | active | README.md, AGENTS.md, repo_protocol_standard.yaml, CHANGELOG.md, docs/index.md |
| ai-anime-short-factory-external | active | README.md, AGENTS.md, repo_protocol_standard.yaml, CHANGELOG.md, docs/index.md |
| api-mini-labs | active | AGENTS.md, repo_protocol_standard.yaml, CHANGELOG.md, docs/index.md |
| audiobook-cleaner-lab | active | repo_protocol_standard.yaml, CHANGELOG.md, docs/index.md |
| resilient-personal-network | active | AGENTS.md, repo_protocol_standard.yaml, CHANGELOG.md, docs/index.md |
| tool-mini-labs | active | AGENTS.md, repo_protocol_standard.yaml, CHANGELOG.md, docs/index.md |
| typing-practice-app | active | AGENTS.md, repo_protocol_standard.yaml, CHANGELOG.md, docs/index.md |
| youtube_hq_downloader | active | AGENTS.md, repo_protocol_standard.yaml, docs/index.md |

## 建议执行顺序

1. 高优先级且缺失 `AGENTS.md` / `repo_protocol_standard.yaml` 的 active 仓库
2. 仅有 README/CHANGELOG 缺失的中优先级仓库
3. archived / missing 路径 — Human 决策是否保留登记

## 生成的 Cursor Prompt

见 `prompts/generated/<repo>_protocol_sync.md`（需 `--no-dry-run` 写入）。
