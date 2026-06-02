# Repo Ops Dashboard

个人多仓库治理层 / Personal Agent OS / Portfolio Orchestrator。

## 项目定位

`repo-ops-dashboard` 是用户个人项目治理层。它读取多个本地仓库的管理文件，汇总组合状态，判断优先级，识别卡点，生成 `task_spec`、handoff packet、proof_of_work 要求、review_queue 决策项和日报/周报。

它不是业务产品，不是普通 Web 应用，也不是第三个编程 Agent。Cursor、Codex、OpenClaw 和业务项目 Agent 负责执行；本项目负责“该做什么、为什么做、谁来做、如何验收”。

## 核心职责

1. 项目注册与生命周期管理
2. Portfolio state 快照
3. 治理任务 intake 与优先级排序
4. task_spec 标准化
5. handoff 给 Cursor/Codex/OpenClaw
6. agent_run.jsonl 审计轨迹设计
7. proof_of_work 验收证据
8. review_queue 人工决策队列
9. execpolicy 权限边界
10. repo_context_index 防止上下文爆炸
11. eval gate 与本地 Dashboard 验证
12. playbook / skill / project_rule 经验沉淀

## 不做什么

- 不直接写小说、翻译、生成视频或发布内容
- 不替代 Cursor/Codex
- 不自动修改被管理业务仓库
- 不全量扫描业务源码
- 不读取 `.env`、密钥、Token、账号文件
- 不自动删除、归档、发布、提交或推送
- 不在治理轮调用外部大模型 API

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python3 -m playwright install chromium

python3 scripts/agent_gate.py
python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/generate_dashboard.py --input data/repo_status.example.json --output dashboard/index.html
python3 scripts/generate_report.py --input data/repo_status.example.json --output reports/daily_repo_report.md
python3 scripts/ui_check.py --file dashboard/index.html --screenshot reports/ui_screenshots/dashboard.png --headless true
```

## 关键目录

- `governance/`：机器可读治理资产、task_spec、proof_of_work、review_queue、execpolicy、eval registry。
- `config/`：仓库登记与扫描/评分配置。
- `scripts/`：扫描、分析、报告、Dashboard、gate 与可选集成脚本。
- `dashboard/`：本地静态视图。
- `docs/`：架构、协议、路线与集成设计。
- `round_state/`：当前轮次和历史。
- `reports/`：审计、日报、周报、完成报告和验证报告。

## 当前状态

- 历史 Round 00-24 已形成扫描、分析、Dashboard、Prompt、报告、Feishu/OpenRouter opt-in、Hub 等基础能力。
- Round 25 将项目重新基线为 Personal Agent OS / Portfolio Orchestrator。
- 真实登记：`config/repos.yaml`。
- 示例登记：`governance/project_registry.example.yaml`。
- 长期路线：`docs/roadmap_40_rounds.md`。

## Workspace MCP Servers

本项目在 Cursor 中需要启用以下 **Workspace MCP Servers**（声明于 `.cursor/mcp.json`）：

| Server | 用途 |
|--------|------|
| **chrome-devtools** | 浏览器调试、console、network、页面状态 |
| **context7** | 第三方库/框架文档查询 |
| **filesystem** | 当前项目目录内文件读写与检查 |
| **github** | 仓库、分支、issue、PR 等 GitHub 操作 |
| **playwright** | 浏览器自动化与 E2E 验收 |

说明：

1. `.cursor/mcp.json` 是本项目的 Workspace MCP 配置；合并已有 server 时勿覆盖无关项。
2. Cursor 可能需要**完全退出并重启**（或重新加载窗口）后才能识别新配置。
3. **GitHub MCP** 需通过环境变量提供 token（如 `GITHUB_TOKEN` → `${env:GITHUB_TOKEN}`），**不允许**写进仓库。
4. **filesystem MCP** 仅授权当前项目目录（配置为 `"."`，相对工作区根）。
5. 运行 `npm run check:mcp`（或 `node scripts/check_mcp_config.js`）做静态配置检查。

详见 `docs/agent_skills/mcp_usage_skill.md` 与 `AGENTS.md` MCP Tools 章节。

## 安全边界

本项目默认只读取被管理仓库 allowlist 管理文件。任何冻结、归档、删除、预算、发布、协议修改、skill/playbook 推广都必须由 HumanOwner 在 review_queue 中确认。
