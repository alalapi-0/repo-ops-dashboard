# 仓库生命周期规则

本仓库**不自动删除**被管理项目目录，仅通过扫描与分析给出状态与归档建议。

## 状态（Round 37 规范）

| 状态 | 含义 |
|------|------|
| `idea` | 未匹配 registry 或早期构思阶段 |
| `bootstrap` | 元项目或初始化中（如 repo-ops-dashboard） |
| `active` | 路径存在且非空，正常推进 |
| `blocked` | 存在 blockers（缺失关键治理文件等） |
| `maintenance` | active 但健康分低于维护阈值 |
| `frozen` | 冻结候选（原 `freeze_candidate` 标记统一为 frozen） |
| `archived` | 归档候选（`missing` / `empty` / `archive_candidate`） |
| `abandoned` | registry 标记为 abandoned，仅人工维护 |

扫描阶段仍会输出 `status=missing` / `empty`；分析器 `lifecycle_status` 将其映射为 `archived`。

机器可读规则见 `config/lifecycle_policy.yaml` 与 [`docs/lifecycle_policy_design.md`](lifecycle_policy_design.md)。

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
