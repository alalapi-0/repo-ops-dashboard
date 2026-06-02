# Budget & Cost Tracking Design

## 目标

按项目记录预算与模型/API 使用**估算**；无 billing API Key 时使用 mock 占位费率，不阻断治理流程。

## 机器可读资产

| 文件 | 说明 |
|------|------|
| `config/budget_tracking_policy.yaml` | 策略：mock 费率、预警阈值、输出路径 |
| `governance/budget_cost_tracking.yaml` | 各项目估算成本与 utilization |
| `reports/budget_cost_tracking.md` | 人类可读汇总 |

## 脚本

```bash
python3 scripts/track_budget_cost.py          # dry-run 默认
python3 scripts/track_budget_cost.py --write  # 写入 YAML 与报告
python3 scripts/validate_budget_tracking_policy.py
```

## 安全与 HITL

- 不读取 `.env`、不调用外部 billing API（`allow_external_billing_api: false`）。
- 预算增加需 HumanOwner 审批；脚本仅生成估算与 `budget_warning` 标记。
- `portfolio_state.summary.budget_warning` 可在后续轮次与真实数据对接。

## Mock 估算逻辑

- active/bootstrap 等项目：`estimated_runs × per_agent_run[agent]`
- archived/missing 等项目：`estimated_runs = 0`
- `utilization_pct >= warning_threshold_pct` 时标记 `budget_warning: true`
