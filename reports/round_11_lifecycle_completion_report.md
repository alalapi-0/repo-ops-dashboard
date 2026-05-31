# Round 11 - Repository Lifecycle Rules 完成报告

- 轮次：`round_11_repository_lifecycle_rules`
- 执行者：cursor
- 外部 API：false（Feishu 发送仍为 opt-in）

## 规则落地

| 条件 | 扫描 status | 分析 lifecycle | archive_candidate |
|------|---------------|----------------|-------------------|
| 路径不存在 | `missing` | `archived` | true |
| 目录为空 | `empty` | `archived` | true |

文档：[`docs/lifecycle_rules.md`](../docs/lifecycle_rules.md)  
规则：[`config/scoring_rules.yaml`](../config/scoring_rules.yaml)

## 代码变更

- `scripts/scan_repos.py`：`is_repository_empty()`
- `scripts/analyze_repos.py`：归档逻辑、`priority_hint` 传递
- `scripts/generate_dashboard.py`：过滤器增加 `empty` / `archived`

## 下游集成

- [`docs/downstream_integrations.md`](../docs/downstream_integrations.md)
- Feishu 发送：[`docs/feishu_integration_plan.md`](../docs/feishu_integration_plan.md)

## 下一步

- Round 10：pytest / `agent_gate` 硬化（可选）
- Human：配置 `FEISHU_WEBHOOK_URL` 后试 `--send`
