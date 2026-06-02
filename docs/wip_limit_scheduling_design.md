# WIP Limit & Scheduling Design

## 目标

限制 portfolio 内 `in_progress` 任务数量，防止多项目并行失控；超限时生成**调度建议**，不自动修改 task queue。

## 机器可读资产

| 文件 | 说明 |
|------|------|
| `config/wip_limit_policy.yaml` | 策略：WIP 上限、计数 status、调度规则 |
| `governance/wip_limit_status.yaml` | 当前 WIP 计数与 defer 建议 |
| `reports/wip_limit_scheduling.md` | 人类可读报告 |

## 脚本

```bash
python3 scripts/check_wip_limit.py          # dry-run 默认
python3 scripts/check_wip_limit.py --write  # 写入 YAML 与报告
python3 scripts/validate_wip_limit_policy.py
```

## 计数逻辑

- 来源：`governance/governance_task_queue.yaml` 中 status ∈ `count_statuses`（默认 `in_progress`, `active`）
- 联动：`portfolio_state.summary.current_wip` 取较大值作为 `effective_wip`
- 超限：按 priority 从低到高建议 `defer`（最低优先级先 defer）

## 安全边界

- 不自动修改 `governance_task_queue.yaml` 或业务仓库。
- HumanOwner 审阅 `deferral_suggestions` 后手动更新任务状态。
