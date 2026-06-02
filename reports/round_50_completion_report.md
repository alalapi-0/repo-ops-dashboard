# Round 50 Completion Report — Skill / Playbook Candidate Extraction

## 目标

从成功任务提取 playbook 候选，人工批准（本阶段 dry-run / autoApprove 默认通过）。

## 推进内容

- 新增 `playbook_extraction_policy.yaml` 与 `extract_playbook_candidates.py`。
- 生成 `governance/playbook_candidates.yaml` 与 `docs/playbook_extraction_design.md`。
- `refresh_status.sh`、`agent_gate` 与 eval registry 纳入 playbook 候选提取验收。

## 验证

```bash
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_playbook_extraction.py -q
python3 scripts/extract_playbook_candidates.py
./scripts/refresh_status.sh --example --ui-check
```

## 下一轮

Round 51：`round_51_project_rule_promotion`。
