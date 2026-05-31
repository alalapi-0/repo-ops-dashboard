# Round 22 - OpenRouter LLM Summary (Opt-in)

## 目标

- `scripts/generate_llm_summary.py`：dry-run 默认，`--call` opt-in
- `refresh_status.sh --llm-summary [--call]`
- OpenRouter 环境变量与 `.env.example` 对齐

## 不做什么

- 不新增 pip 依赖
- 不默认调用外部 API

## 验收标准

- `pytest tests/test_generate_llm_summary.py` PASS
- dry-run 写 `reports/llm_daily_summary.md`
- `--call` 需 `LLM_ENABLED=true` 与 `OPENROUTER_API_KEY`

## 推荐执行 Agent

- Cursor

## 可复制给 Cursor 的任务摘要

实现 generate_llm_summary.py（stdlib HTTP）；接入 refresh；补测试。
