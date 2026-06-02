# Round 37 Completion Report — Lifecycle Rules

## 目标

实现 idea/bootstrap/active/blocked/maintenance/frozen/archived/abandoned 生命周期规则。

## 推进内容

- 新增 `config/lifecycle_policy.yaml` 与 `governance/lifecycle_policy.example.yaml`。
- 新增 `scripts/validate_lifecycle_policy.py`、`read_lifecycle_policy.py`。
- `analyze_repos.py` 默认加载 lifecycle policy，经 `derive_lifecycle_v1` 输出规范 `lifecycle_status`。
- 更新 `docs/lifecycle_rules.md`、`docs/lifecycle_policy_design.md`。
- `agent_gate` 与 eval registry 增加 `lifecycle_policy` 验收。
- 新增 `tests/test_lifecycle_policy.py`。

## 验证

```bash
npm run check:mcp
python3 scripts/read_lifecycle_policy.py
python3 scripts/validate_lifecycle_policy.py
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_lifecycle_policy.py tests/test_analyze_repos.py -q
./scripts/refresh_status.sh --example --ui-check
```

## 下一轮

Round 38：`round_38_blocker_management`（卡点管理）。
