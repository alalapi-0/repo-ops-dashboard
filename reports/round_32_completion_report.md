# Round 32 Completion Report — Execpolicy Checker

## 目标

将 execpolicy 文档约束部分脚本化。

## 推进内容

- 新增 `scripts/validate_execpolicy.py`：解析 `.rules` 语法、校验 portfolio 必选 deny/prompt 规则与三个 profile。
- 新增 `scripts/read_execpolicy.py`、`scripts/check_execpolicy_action.py`（路径/命令 dry-run 分类）。
- `agent_gate` 增加 `execpolicy` 检查；eval registry 增加 `execpolicy_valid`。
- 更新 `docs/execpolicy_design.md`、`governance/README.md`、`docs/data_models.md`。
- 新增 `tests/test_execpolicy.py`。

## 验证

```bash
npm run check:mcp
python3 scripts/read_execpolicy.py --all
python3 scripts/check_execpolicy_action.py --profile risky_confirm --command "git push" --dry-run
python3 scripts/check_execpolicy_action.py --profile readonly_managed_repo --action read --path README.md --dry-run
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_execpolicy.py -q
./scripts/refresh_status.sh --example --ui-check
```

## 下一轮

Round 33：`round_33_repo_context_index_mvp`（轻量 repo_context_index）。
