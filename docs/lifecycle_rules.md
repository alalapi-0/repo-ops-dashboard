# 仓库生命周期规则

本仓库**不自动删除**被管理项目目录，仅通过扫描与分析给出状态与归档建议。

## 状态

| 状态 | 含义 |
|------|------|
| `active` | 路径存在且非空，正常推进 |
| `bootstrap` | 元项目或初始化中（如 repo-ops-dashboard） |
| `missing` | 登记路径不存在（常见于已手动删除的低优先级项目） |
| `empty` | 路径存在但目录内无有效文件（忽略 `.git`、`.DS_Store`） |
| `archived` | 分析器判定为归档候选（`missing` 或 `empty`） |
| `freeze_candidate` | 健康分过低或长期无治理文件 |

## 自动归档候选（无需 Human 确认即可标记）

以下情况 `archive_candidate=true`，`lifecycle_status=archived`，`recommended_agent=Human`：

1. **路径缺失**（`status=missing`）：登记保留，扫描标缺失，Dashboard 显示 Archive。
2. **目录为空**（`status=empty`）：同上，建议从 `config/repos.yaml` 复核或删除登记行。

**禁止**：脚本自动 `rm -rf` 或修改业务仓库内文件。

## Human 操作

- 确认归档：可保留 yaml 条目作历史，或删除 `config/repos.yaml` 中对应 `name`。
- 重新激活：恢复目录与内容后重新扫描即可。
- 优先级：在 `repos.yaml` 中调整 `priority_hint`（`high` / `medium` / `low`）。

## 与扫描脚本的关系

- [`scripts/scan_repos.py`](../scripts/scan_repos.py)：`missing` / `empty` 在扫描阶段判定。
- [`scripts/analyze_repos.py`](../scripts/analyze_repos.py)：写入 `archive_candidate` 与 `lifecycle_status`。
- 新目录：[`scripts/sync_repo_registry.py`](../scripts/sync_repo_registry.py) 合并进登记，不覆盖已有 `priority_hint`。
