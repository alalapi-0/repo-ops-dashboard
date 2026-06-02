# Round 34 Completion Report — Readonly Repo Scanner V2

## 目标

严格 allowlist 扫描 README/AGENTS/协议/round_state。

## 推进内容

- 新增 `config/scan_policy.yaml` 与 `governance/scan_policy.example.yaml`（v2 核心治理分类）。
- 新增 `scripts/validate_scan_policy.py`、`read_scan_policy.py`。
- `scan_repos.py` 增加 `scanner_version`、`core_governance`、`file_categories` 输出；默认加载 scan policy。
- `agent_gate` 增加 `scan_policy` 检查；eval registry 增加 `scan_policy_valid`。
- 更新 `docs/scan_policy_design.md`、`governance/README.md`。
- 新增 `tests/test_scan_repos.py`。

## 验证

```bash
npm run check:mcp
python3 scripts/read_scan_policy.py
python3 scripts/validate_scan_policy.py
python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python3 scripts/agent_gate.py
.venv/bin/python -m pytest tests/test_scan_repos.py -q
./scripts/refresh_status.sh --example --ui-check
```

## 下一轮

Round 35：`round_35_status_analyzer_v2`（状态分析器 v2）。
