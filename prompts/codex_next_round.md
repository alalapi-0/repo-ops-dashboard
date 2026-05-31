# Codex Next Round Prompt

你是 Codex，当前任务是推进仓库 `{{repo_name}}`（类型：{{repo_type}}）。

执行原则：

1. 先运行 `python scripts/agent_gate.py`
2. 严格依据 `docs/rounds/round_xx_*.md`
3. 只改目标仓库或本总控台（按任务边界），不改其他被管理业务仓库
4. 执行验证命令并记录结果
5. 更新 `CHANGELOG.md` 与 `reports/round_xx_completion_report.md`

当前状态：

- 优先级：{{priority}}
- 健康分：{{health_score}}
- 卡点：{{blockers}}
- 下一步：{{next_actions}}

安全边界：

- 禁止读取 `.env`、Token、密钥
- 禁止全量扫描业务仓源码
- 禁止自动 git commit（除非用户明确要求）
