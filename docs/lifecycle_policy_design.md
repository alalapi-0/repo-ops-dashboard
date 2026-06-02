# Lifecycle Policy Design (Round 37)

## 状态集合

`idea` · `bootstrap` · `active` · `blocked` · `maintenance` · `frozen` · `archived` · `abandoned`

## 判定顺序（`analyze_repos.derive_lifecycle`）

1. registry `lifecycle=abandoned` → **abandoned**
2. registry `lifecycle=idea` → **idea**
3. `archive_candidate` 或 `status` 为 missing/empty → **archived**
4. 存在 blockers → **blocked**
5. `freeze_candidate` → **frozen**（取代旧字符串 `freeze_candidate`）
6. `status=bootstrap` → **bootstrap**
7. active 且 `health_score < threshold` → **maintenance**
8. 未匹配 registry → **idea**
9. 默认 → **active**

## 配置

- Live：`config/lifecycle_policy.yaml`
- 示例：`governance/lifecycle_policy.example.yaml`
- 校验：`scripts/validate_lifecycle_policy.py`

人类可读说明见 [`docs/lifecycle_rules.md`](lifecycle_rules.md)。

## 安全边界

仅标记状态，不自动删除目录、不修改被管理业务仓库。
