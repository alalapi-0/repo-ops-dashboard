# Round 51 Completion Report — Project Rule Promotion

## 目标

将成功规则推广到项目规则，进入 review_queue（默认仅生成 promotion_queue，不自动合并）。

## 推进内容

- 新增 `project_rule_promotion_policy.yaml` 与 `promote_project_rule.py`。
- 生成 `governance/project_rule_promotion_queue.yaml` 与 `docs/project_rule_promotion_design.md`。
- `refresh_status.sh`、`agent_gate` 与 eval registry 纳入 project_rule 推广验收。

## 验证

```bash
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_project_rule_promotion.py -q
python3 scripts/promote_project_rule.py
./scripts/refresh_status.sh --example --ui-check
```

## 下一轮

Round 52：`round_52_cross_repo_protocol_sync_suggestion`。
