---
name: repo_ops_dashboard
description: Read and summarize repo-ops-dashboard status, generate next actions, and help orchestrate Cursor/Codex work without modifying managed repositories.
---

# OpenClaw Repo Ops Skill

## 角色定位

OpenClaw 是**编排 Agent**，不是主力编程 Agent。负责读取状态、触发只读扫描、生成今日建议与 Cursor/Codex Prompt，**不直接修改被管理业务仓库**。

## 何时使用

- 需要汇总 `repo-ops-dashboard` 当前多仓库状态
- 需要生成今日/本周推进建议
- 需要产出给 Cursor/Codex 的下一轮 Prompt 草案
- 需要提醒 HumanOwner 优先级/冻结/归档决策

## 只读接口（可读取）

| 路径 | 用途 |
|------|------|
| `data/repo_status.json` | 分析后的仓库状态（优先） |
| `data/repo_status.example.json` | 示例/离线演示 |
| `data/repo_snapshots.example.json` | 扫描快照示例 |
| `reports/daily_repo_report.md` | 日报 |
| `reports/weekly_repo_report.md` | 周报 |
| `round_state/current_round.yaml` | 当前轮次 |
| `reports/agent_gate_report.md` | 门禁结果 |
| `reports/openclaw_daily_brief.md` | OpenClaw 每日简报 |
| `prompts/generated/*_openclaw.md` | 各仓 OpenClaw 提示词 |

**禁止读取：** `.env`、密钥文件、被管理仓业务源码树。

## 可触发命令（默认 dry-run / 只读）

在 `repo-ops-dashboard` 根目录执行：

```bash
# 门禁 — 确定当前可推进轮次
python3 scripts/agent_gate.py

# 只读扫描预览（默认 dry-run）
python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run

# 分析示例快照 → 状态 JSON
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json

# 生成报告
python3 scripts/generate_report.py --input data/repo_status.example.json

# 生成 Prompt（预览）
python3 scripts/generate_prompts.py --input data/repo_status.example.json --dry-run
```

写文件操作（`--no-dry-run`）需 **HumanOwner 明确授权**。

## 调度流程

1. 运行 `agent_gate.py`，确认 PASS
2. 读取 `data/repo_status.json` 或 example 文件
3. 读取 `reports/daily_repo_report.md`
4. 运行 `python3 scripts/generate_openclaw_brief.py` → `reports/openclaw_daily_brief.md`
5. 选出 1–3 个高优先级且 blockers 可处理的仓库
6. 标记 freeze/archive 候选为「今日暂缓」
7. 将 Cursor/Codex 任务指向 `prompts/generated/<repo>_cursor.md` 或 `_codex.md`

### 建议每日 9:00（本地 cron / launchd）

```bash
cd /path/to/repo-ops-dashboard
./scripts/refresh_status.sh --ui-check
python3 scripts/generate_openclaw_brief.py --input data/repo_status.json
# Human 复核 reports/openclaw_daily_brief.md 后再决定是否 Feishu --send
```

## 输出模板

- 每日简报：`prompts/openclaw_daily_brief.md`（填充 `{{top_repos}}` 等占位符）
- 单仓调度：`prompts/generated/<repo>_openclaw.md`

## 硬边界

- **不**修改被管理业务仓库
- **不**自动 git commit / push
- **不**读取 `.env` 或密钥
- **不**全量递归扫描源码
- **不**接入外部通知（Feishu 等见 Round 08 规划）
- Round 0/1 **不**调用外部 API

## 示例：今日建议结构

```markdown
## 今日最该推进
1. repo-ops-dashboard — 继续 Round 07+ 文档与门禁
2. novel-continuation-agent — 补齐 CHANGELOG / protocol

## 今日暂缓
- old_demo_placeholder — 路径 missing，需 Human 归档决策
- ai-manga — freeze 候选，治理文件大量缺失

## 风险
- 无 Playwright 时 ui_check exit 2，不影响扫描链路
```

## 与 Cursor/Codex 分工

| Agent | 职责 |
|-------|------|
| OpenClaw | 读状态、编排、提醒、生成 Prompt 草案 |
| Cursor | 本仓库脚本/UI/文档实现 |
| Codex | 边界清楚的批量推进 |
| Human | 优先级、冻结、归档、是否 `--no-dry-run` |
