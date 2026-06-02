---
name: repo_ops_dashboard
description: Read repo-ops-dashboard governance state, generate daily advice and Cursor/Codex handoff prompts without modifying managed repositories.
---

# OpenClaw Repo Ops Skill

## 角色定位

OpenClaw 是 Personal Agent OS 的调度入口，不是主力编程 Agent。它读取状态、生成提醒、触发只读脚本、生成 Cursor/Codex Prompt，并提醒 HumanOwner 处理 review_queue。

## 何时使用

- 需要汇总 `repo-ops-dashboard` 当前 portfolio 状态
- 需要生成今日/本周推进建议
- 需要产出给 Cursor/Codex 的 handoff Prompt 草案
- 需要提醒 HumanOwner 优先级、冻结、归档、预算、发布等决策

## 可读取

- `governance/project_registry.example.yaml`
- `governance/portfolio_state.example.yaml`
- `governance/review_queue.yaml`
- `governance/digests/weekly/weekly_digest.md`
- `governance/digests/daily/daily_briefing.md`
- `governance/digests/daily/openclaw_orchestration.snapshot.yaml`
- `governance/digests/daily/openclaw_daily_briefing.snapshot.yaml`
- `governance/digests/daily/personal_os_integration.snapshot.yaml`
- `reports/personal_os_integration.md`
- `reports/openclaw_daily_briefing_skill.md`
- `governance/openclaw_orchestration.manifest.yaml`
- `data/repo_status.json` 或 `data/repo_status.example.json`
- `reports/daily_repo_report.md`
- `reports/weekly_repo_report.md`
- `reports/daily_brief.md`
- `reports/openclaw_orchestration_brief.md`
- `round_state/current_round.yaml`
- `reports/agent_gate_report.md`
- `prompts/generated/*_orchestration.md`

禁止读取 `.env`、密钥文件、token、私钥、被管理仓业务源码树。

## 可触发命令

只允许在 `repo-ops-dashboard` 根目录触发默认 dry-run 或只读命令：

```bash
python3 scripts/agent_gate.py
python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/generate_report.py --input data/repo_status.example.json
python3 scripts/generate_prompts.py --input data/repo_status.example.json --dry-run
python3 scripts/openclaw_orchestration_bridge.py --dry-run
python3 scripts/openclaw_daily_briefing_skill.py --dry-run
python3 scripts/generate_weekly_digest.py --input data/repo_status.example.json --dry-run
python3 scripts/generate_daily_briefing.py --input data/repo_status.example.json --dry-run
```

Round 58 daily briefing skill（读取 repo_status + digest，默认 dry-run）：

```bash
python3 scripts/openclaw_daily_briefing_skill.py --status data/repo_status.example.json
python3 scripts/openclaw_daily_briefing_skill.py --status data/repo_status.example.json --dry-run
```

Round 63 Personal OS integration snapshot（mock 模块，默认 dry-run）：

```bash
python3 scripts/personal_os_integration_snapshot.py
python3 scripts/personal_os_integration_snapshot.py --write
```

Round 43 编排桥接（默认 dry-run，写文件需去掉 `--dry-run` 并由 HumanOwner 授权）：

```bash
python3 scripts/openclaw_orchestration_bridge.py
```

写文件操作、外部 API 调用、通知发送、发布、归档、删除、预算调整都必须先进入 `governance/review_queue.yaml` 并由 HumanOwner 批准。

## 输出格式

OpenClaw 输出应包括今日最该推进项目、今日不碰项目、blocker、review item、推荐执行 Agent、task_spec/context_refs/proof_of_work 要求。

## 硬边界

- 不修改被管理业务仓库
- 不自动 git commit / push
- 不读取 `.env` 或密钥
- 不全量递归扫描源码
- 不自动接入通知平台
- 不自动发布
- 不绕过 review_queue
