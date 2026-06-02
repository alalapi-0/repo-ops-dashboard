# Round 31 Completion Report — Review Queue MVP

## 目标

实现 `review_queue` 读写与人工决策状态校验。

## 推进内容

- 新增 `scripts/validate_review_queue.py`：校验队列结构与 HITL 规则（open 项 decision 必须为 null）。
- 新增 `scripts/read_review_queue.py`、`add_review_queue_item.py`、`close_review_queue_item.py`（关闭仅 `--actor human_owner`）。
- 新增 `governance/review_queue.example.yaml`。
- `agent_gate` 增加 `review_queue` 检查；eval 增加 `review_queue_valid`。
- 更新 `docs/data_models.md`、`governance/README.md`。
- 新增 `tests/test_review_queue.py`。

## 验证

```bash
npm run check:mcp
python3 scripts/read_review_queue.py --status open
python3 scripts/add_review_queue_item.py --review-id rq_dry_run_test --type governance_policy --task-id task_round_31 --prompt "test?" --options approve,reject --dry-run
python3 scripts/close_review_queue_item.py --review-id rq_001_personal_agent_os_positioning --decision approve --actor human_owner --dry-run
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_review_queue.py -q
./scripts/refresh_status.sh --example --ui-check
```

## 下一轮

Round 32：`round_32_execpolicy_checker`（execpolicy 检查器）。
