# Round 36 Completion Report — Priority Scoring System

## 目标

实现 impact × urgency × unblock - cost - risk 评分。

## 推进内容

- 新增 `config/priority_scoring_policy.yaml` 与 `governance/priority_scoring_policy.example.yaml`。
- 新增 `scripts/priority_scoring.py`、`validate_priority_scoring_policy.py`、`read_priority_scoring_policy.py`。
- `analyze_repos.py` 输出 `priority_score`、`priority_score_band`、`priority_score_breakdown`。
- `sync_portfolio_state.py`、`generate_dashboard.py` 展示治理评分。
- `agent_gate` 与 eval registry 增加 `priority_scoring_policy` 验收。
- 新增 `docs/priority_scoring_design.md`、`tests/test_priority_scoring.py`。

## 验证

```bash
npm run check:mcp
python3 scripts/read_priority_scoring_policy.py
python3 scripts/validate_priority_scoring_policy.py
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_priority_scoring.py tests/test_analyze_repos.py -q
./scripts/refresh_status.sh --example --ui-check
```

## 下一轮

Round 37：`round_37_lifecycle_rules`（生命周期规则 v1）。
