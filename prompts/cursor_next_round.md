# Cursor Next Round Prompt

你是 Cursor，当前仓库是 `repo-ops-dashboard`。

请按以下顺序执行：

1. 读取 `repo_protocol_standard.yaml`
2. 读取 `round_state/current_round.yaml`
3. 读取对应 `docs/rounds/` 文档
4. 先跑 `python scripts/agent_gate.py`
5. 基于 `data/repo_status.json` 推进下一轮脚本或 Dashboard 改进
6. 更新 `CHANGELOG.md`、`round_state/`、`reports/`

约束：

- 不读取 `.env` 与密钥文件
- 不修改被管理业务仓库
- 默认 dry-run
