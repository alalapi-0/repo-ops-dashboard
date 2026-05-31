# Cursor Next Round Prompt

你是 Cursor，当前仓库是 `{{repo_name}}`（类型：{{repo_type}}）。

请按以下顺序执行：

1. 读取 `repo_protocol_standard.yaml`
2. 读取 `round_state/current_round.yaml`
3. 读取对应 `docs/rounds/` 文档
4. 先跑 `python scripts/agent_gate.py`
5. 基于仓库状态推进下一轮脚本或 Dashboard 改进
6. 更新 `CHANGELOG.md`、`round_state/`、`reports/`

当前状态：

- 优先级：{{priority}}
- 健康分：{{health_score}}
- 阶段：{{current_stage}}
- 卡点：{{blockers}}
- 下一步：{{next_actions}}
- 扫描 warning：{{warnings}}

约束：

- 不读取 `.env` 与密钥文件
- 不修改被管理业务仓库
- 默认 dry-run
