# Round 48 Completion Report — Failure Recovery & Retry Policy

## 目标

定义 retry_count、failure_class、checkpoint_id、review_queue 升级。

## 推进内容

- 新增 `config/failure_recovery_policy.yaml` 与 `governance/failure_recovery_policy.example.yaml`。
- 新增 `validate_failure_recovery_policy.py`、`failure_recovery.py` 与 `docs/failure_recovery_design.md`。
- `refresh_status.sh`、`agent_gate` 与 eval registry 纳入 failure recovery 验收。

## 验证

```bash
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_failure_recovery_policy.py -q
python3 scripts/failure_recovery.py --task-id task_example --failure-class validation_failed --retry-count 1
./scripts/refresh_status.sh --example --ui-check
```

## 恢复命令

```bash
cd /Users/alalapi/PycharmProjects/repo-ops-dashboard
python3 scripts/validate_failure_recovery_policy.py
python3 scripts/failure_recovery.py --json --task-id task_example --failure-class transient --retry-count 0
```

## 下一轮

Round 49：`round_49_checkpoint_snapshot`。
