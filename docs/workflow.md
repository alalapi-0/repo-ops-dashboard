# 工作流

## Round 执行流程

1. 读取 `repo_protocol_standard.yaml`
2. 读取 `round_state/current_round.yaml`
3. 读取对应 `docs/rounds/` 文档
4. 产出计划并确认范围
5. 执行有限修改
6. 运行验证命令
7. 更新 `CHANGELOG.md` 与 `round_state/`
8. 生成 completion report

## 默认命令链

```bash
python scripts/agent_gate.py
python scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python scripts/generate_dashboard.py --input data/repo_status.example.json --output dashboard/index.html
python scripts/generate_report.py --input data/repo_status.example.json --output reports/daily_repo_report.md
```
