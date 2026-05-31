# 本地调度说明（Round 06）

本仓库提供脚本链路，**不自动部署 cron**。用户可在本地用 cron 或 launchd 定期运行。

## 推荐流水线

```bash
cd /path/to/repo-ops-dashboard
source .venv/bin/activate  # 可选

python3 scripts/scan_repos.py --config config/repos.example.yaml --no-dry-run
python3 scripts/analyze_repos.py
python3 scripts/generate_dashboard.py
python3 scripts/generate_report.py
python3 scripts/generate_prompts.py --no-dry-run
python3 scripts/ui_check.py --file dashboard/index.html --headless true
```

## macOS launchd 示例（每日 09:00）

将 `com.user.repo-ops-dashboard.plist` 放入 `~/Library/LaunchAgents/`，ProgramArguments 指向上述脚本或包装 shell。

## 注意

- 默认使用 `config/repos.example.yaml`；真实环境请复制为 `config/repos.yaml`（勿提交敏感路径）
- 报告输出在 `reports/`，本地数据在 `data/`（部分已 gitignore）
- 不接 Feishu/Telegram/外部通知（见 Round 08 规划）
