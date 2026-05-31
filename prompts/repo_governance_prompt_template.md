# Repo Governance Prompt Template

你正在推进 `{round_id}`。

请先阅读：

- `repo_protocol_standard.yaml`
- `AGENTS.md`
- `round_state/current_round.yaml`
- `docs/rounds/{round_doc}`

任务：

1. 输出计划
2. 在边界内执行修改
3. 运行验证命令
4. 更新 `CHANGELOG.md`
5. 生成 `reports/{round_id}_completion_report.md`

禁止：

- 读取 `.env`、密钥、Token
- 修改被管理业务仓库
- 外部 API 写入
