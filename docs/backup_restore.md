# 备份、恢复与迁移

> 仅备份治理层 YAML/JSON 资产，**不包含** `.env`、密钥或被管理业务仓库。

## 备份

默认 dry-run（只输出报告，不复制文件）：

```bash
python3 scripts/backup_governance_state.py
```

写入备份到 `governance/backups/<backup_id>/`：

```bash
python3 scripts/backup_governance_state.py --write
```

备份范围见 [`config/backup_restore_policy.yaml`](../config/backup_restore_policy.yaml) 的 `include_paths`：

- `governance/portfolio_state.yaml`
- `governance/project_registry.yaml`
- `governance/review_queue.yaml`
- `round_state/current_round.yaml`
- 相关 config policy

## 恢复（需 HITL）

1. HumanOwner 审阅 `governance/backups/manifest.yaml` 选择目标 `backup_id`。
2. 手动复制所需文件到对应路径（**不覆盖**未经审阅的 live 文件）。
3. 运行 `python3 scripts/agent_gate.py` 验证。
4. 运行 `./scripts/refresh_status.sh --example --ui-check` 确认 Dashboard 正常。

自动恢复脚本** intentionally 未提供**，避免绕过 HumanOwner 决策。

## 迁移到新机器

1. 克隆仓库：`git clone <repo-url> repo-ops-dashboard`
2. 安装依赖：见 [`installation.md`](installation.md)
3. 复制 `config/repos.yaml`（或从 example 起步）
4. 可选：从备份目录恢复 `governance/*.yaml`
5. 验证：`./scripts/refresh_status.sh --example --ui-check`

## 故障排查

| 问题 | 处理 |
|------|------|
| backup 报告有 missing 文件 | 先运行 `sync_portfolio_state.py` 或检查路径 |
| manifest 条目过多 | policy 中 `max_retained` 自动裁剪 |
| 恢复后 gate 失败 | 对比 `reports/agent_gate_report.md` 逐项修复 |
