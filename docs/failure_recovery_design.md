# Failure Recovery 设计

治理任务失败时的重试、分类、检查点与 review_queue 升级策略。

## 策略文件

- 机器权威：`config/failure_recovery_policy.yaml`
- 示例：`governance/failure_recovery_policy.example.yaml`

## 字段

- `retry.max_retry_count` / `backoff_hours`：可重试失败的最大次数与退避。
- `failure_classes`：`transient`、`validation_failed`、`policy_violation`、`human_required`。
- `checkpoint.id_prefix`：失败时生成的 `checkpoint_id`（如 `ckpt_task_x_r1`）。
- `review_queue_escalation`：按 `retry_count` 升级至 `create_review_queue_item` 或 `require_human_owner_decision`。

## 脚本

```bash
python3 scripts/validate_failure_recovery_policy.py
python3 scripts/failure_recovery.py --task-id task_example --failure-class validation_failed --retry-count 1
```

默认 dry-run，不调用外部 API，不修改被管理业务仓库。
