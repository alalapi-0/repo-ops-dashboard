# Cross-Repo Protocol Sync Suggestion Design

## 目标

对比被管理仓库快照中的治理文件缺失情况，生成**只读**同步建议，不写入任何业务仓库。

## 机器可读资产

| 文件 | 说明 |
|------|------|
| `config/protocol_sync_policy.yaml` | 策略：输入路径、治理文件清单、优先级规则 |
| `governance/protocol_sync_suggestions.yaml` | 各仓差异与建议优先级（由脚本生成） |
| `reports/protocol_sync_suggestions.md` | 人类可读报告 |
| `prompts/generated/<repo>_protocol_sync.md` | 可选 Cursor Prompt（`--no-dry-run`） |

## 脚本

```bash
python3 scripts/protocol_sync_report.py --input data/repo_snapshots.example.json
python3 scripts/validate_protocol_sync_policy.py
```

## 安全边界

- 不读取 `.env`、密钥或 token。
- 不 `git commit` / `git push` 到被管理仓库。
- 默认 `dry_run=true`；Prompt 写入需显式 `--no-dry-run`。

## HumanOwner 流程

1. 查看 `governance/protocol_sync_suggestions.yaml` 或 Markdown 报告。
2. 选择需同步的仓库与优先级。
3. 在目标仓库内由 Cursor/Codex 手动执行 Prompt，产出 `docs/reports/repo_protocol_sync_report.md`。
