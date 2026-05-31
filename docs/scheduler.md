# 本地调度说明（Round 06）

本仓库提供脚本链路，**不自动部署 cron**。用户可在本地用 cron、launchd 或 Cursor Automations 定期运行。

## 推荐流水线（真实登记）

```bash
cd /path/to/repo-ops-dashboard
source .venv/bin/activate  # 可选

python3 scripts/scan_repos.py --config config/repos.yaml --no-dry-run
python3 scripts/analyze_repos.py
python3 scripts/generate_dashboard.py
python3 scripts/generate_report.py
python3 scripts/generate_prompts.py --no-dry-run
python3 scripts/prepare_feishu_payload.py              # 预览
python3 scripts/prepare_feishu_payload.py --send     # 可选：需 FEISHU_WEBHOOK_URL
python3 scripts/ui_check.py --file dashboard/index.html --headless true
```

新增 PycharmProjects 子目录时：

```bash
python3 scripts/sync_repo_registry.py --workspace /Users/alalapi/PycharmProjects
```

## macOS launchd 示例（每日 09:00）

将 `com.user.repo-ops-dashboard.plist` 放入 `~/Library/LaunchAgents/`，ProgramArguments 指向上述脚本或包装 shell。

## 注意

- 正式环境使用 [`config/repos.yaml`](../config/repos.yaml)（可提交；公开 fork 时请脱敏 path 或改用本地副本）
- 示例链路仍可用 `config/repos.example.yaml` + `data/*.example.json`
- 报告输出在 `reports/`，本地数据在 `data/`（部分已 gitignore）
- 下游集成路线见 [`downstream_integrations.md`](downstream_integrations.md)
