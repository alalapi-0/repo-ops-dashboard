# Round 44 Completion Report — Weekly Digest MVP

## 目标

生成 weekly_digest Markdown。

## 推进内容

- 新增 `scripts/generate_weekly_digest.py`：合并 repo_status、portfolio_state、review_queue、task_queue、round_state、human_notes。
- 新增 `prompts/weekly_digest.md` 与 `tests/test_generate_weekly_digest.py`。
- 输出 `governance/digests/weekly/weekly_digest.md`。
- `refresh_status.sh` 与 `agent_gate` 纳入 weekly_digest 检查。

## 验证

```bash
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_generate_weekly_digest.py -q
.venv/bin/python scripts/generate_weekly_digest.py --input data/repo_status.example.json --dry-run
./scripts/refresh_status.sh --example --ui-check
```

## 下一轮

Round 45：`round_45_daily_briefing_mvp`。
