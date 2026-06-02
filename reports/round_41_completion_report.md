# Round 41 Completion Report — Prompt Generator for Cursor

## 目标

根据 task_spec 生成 Cursor Prompt。

## 推进内容

- 新增 `prompts/cursor_from_task_spec.md` 模板。
- 新增 `scripts/generate_cursor_prompt_from_task_spec.py`（校验必填字段、dry-run 默认）。
- `refresh_status.sh` 纳入 example task_spec 的 dry-run 生成步骤。
- 新增 `tests/test_generate_cursor_prompt_from_task_spec.py`；`agent_gate` 增加 cursor_task_spec_prompt 检查。

## 验证

```bash
npm run check:mcp
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_generate_cursor_prompt_from_task_spec.py -q
.venv/bin/python scripts/generate_cursor_prompt_from_task_spec.py --dry-run
./scripts/refresh_status.sh --example --ui-check
```

## 下一轮

Round 42：`round_42_prompt_generator_for_codex`（根据 task_spec 生成 Codex Prompt）。
