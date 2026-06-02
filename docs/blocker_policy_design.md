# Blocker Policy Design (Round 38)

## Blocker 类型

| type_id | 触发模式 | 严重度 | 默认负责人 |
|---------|----------|--------|------------|
| `governance_missing` | `* missing`（AGENTS.md / protocol / README） | high | Cursor |
| `repository_path` | `repository path missing` | critical | Human |
| `repository_empty` | `repository directory empty` | high | Human |

分类逻辑：`scripts/blocker_management.py` → `classify_blocker()`，按 policy 中 `types[].patterns` 子串匹配。

## 超时升级

按 blocker 存在天数（`age_days`，默认 0）选取最高适用级别：

| level | after_days | action |
|-------|------------|--------|
| info | 0 | log_only |
| warning | 3 | surface_in_dashboard |
| review | 7 | create_review_queue_item |
| hitl | 14 | require_human_owner_decision |

升级仅标记建议动作，不自动创建 review item 或通知 HumanOwner。

## 配置

- Live：`config/blocker_policy.yaml`
- 示例：`governance/blocker_policy.example.yaml`
- 校验：`scripts/validate_blocker_policy.py`
- 分类/升级：`scripts/blocker_management.py`

`analyze_repos.py` 输出 `blocker_details`（含 type、severity、owner、escalation_level）。

## 安全边界

仅分类与标记，不自动修改被管理业务仓库、不读取 `.env`、不触发外部 API。
