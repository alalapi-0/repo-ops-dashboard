# Round 28 Completion Report — Governance Task Queue

## 目标

实现 `governance_task` 队列与 `task_spec` 读取/校验。

## 推进内容

- 新增 `scripts/sync_governance_task_queue.py`：扫描 `governance/task_specs/*.yaml`（排除模板），生成 `governance/governance_task_queue.yaml`。
- 新增 `scripts/read_task_spec.py`：读取并校验单个 task_spec（支持 `--json`）。
- 新增 `governance/governance_task_queue.example.yaml` 与生成后的 `governance_task_queue.yaml`。
- `agent_gate` 增加 `governance_task_queue` 检查；eval 增加 `governance_task_queue_exists`。
- 更新 `docs/data_models.md`、`governance/README.md`。
- 新增 `tests/test_governance_task_queue.py`。

## 验证

```bash
npm run check:mcp
python3 scripts/sync_governance_task_queue.py --dry-run
python3 scripts/read_task_spec.py governance/task_specs/example_task_spec.yaml
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_governance_task_queue.py -q
./scripts/refresh_status.sh --example --ui-check
```

## MCP / 浏览器

- MCP 静态检查通过（5 servers）。
- Dashboard 经 `refresh_status.sh --example --ui-check` 本地 HTTP + ui_check 确认（无 Dashboard 结构变更）。

## 下一轮

Round 29：proof_of_work 模板、生成与校验。
