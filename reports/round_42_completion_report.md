# Round 42 Completion Report — Prompt Generator for Codex

## 目标

根据 task_spec 生成 Codex Prompt。

## 推进内容

- 新增 `prompts/codex_from_task_spec.md` 与 `example_codex_task_spec.yaml`。
- 新增 `scripts/generate_codex_prompt_from_task_spec.py`。
- `refresh_status.sh` 与 `agent_gate` 纳入 Codex task_spec 生成检查。
- 新增 `tests/test_generate_codex_prompt_from_task_spec.py`。

## 验证

```bash
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_generate_codex_prompt_from_task_spec.py -q
.venv/bin/python scripts/generate_codex_prompt_from_task_spec.py --dry-run
```

## 下一轮

Round 43：`round_43_openclaw_orchestration_bridge`。
