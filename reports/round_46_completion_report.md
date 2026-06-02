# Round 46 Completion Report — Eval Registry Script

## 目标

把 eval registry 中基础项脚本化。

## 推进内容

- 新增 `scripts/run_eval_registry.py`：读取 `governance/evals/registry.yaml`，按 type 执行 file_exists / static_scan / policy_check / yaml_check / schema_check / ui_check。
- registry 增加 `runner` 元数据与 `eval_registry_runner_valid` 条目；`completion_report_exists` 改为从 round_state 动态解析。
- `refresh_status.sh` 与 `agent_gate` 纳入 eval registry runner 检查；新增 `tests/test_run_eval_registry.py`。

## 验证

```bash
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_run_eval_registry.py -q
python3 scripts/run_eval_registry.py --required-only
./scripts/refresh_status.sh --example --ui-check
```

## 恢复命令

```bash
cd /Users/alalapi/PycharmProjects/repo-ops-dashboard
python3 scripts/run_eval_registry.py --required-only
python3 scripts/agent_gate.py
```

## 下一轮

Round 47：`round_47_handoff_protocol_implementation`。
