# Repo Ops Dashboard

个人多仓库管理总控台 / 仓库项目经理 / Repo Ops Dashboard。

## 项目定位

`repo-ops-dashboard` 是一个多仓库治理与调度层项目，用于读取多个本地仓库的管理文件，汇总状态并生成可执行推进建议。  
它不是业务产品，不是普通 Web 应用，也不是第三个编程 Agent。

## 为什么它不是编程 Agent

- 本项目本身不承担主力编码执行角色。
- 本项目只聚合状态、生成建议与下一轮提示词。
- 本项目强调治理、安全边界与可持续推进流程。

## 为什么它是多仓库调度层

- 只读取管理文件，不全量读取源码。
- 不改动被管理业务仓库。
- 输出统一状态面板、日报周报、下一轮执行提示。

## Agent 分工

- Cursor：开发本项目、写脚本、调试 UI。
- Codex：执行明确推进轮、批量修改、自动 PR。
- OpenClaw：后续做调度、提醒、入口调用，不承担主力开发。

## 安全边界

- 本项目不会直接修改被管理的业务仓库。
- 本项目默认只读取仓库管理文件。
- 本项目不读取 `.env`、密钥、Token、账号文件。
- Round 0 不调用外部 API，不接真实通知平台。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/agent_gate.py
python scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python scripts/generate_dashboard.py --input data/repo_status.example.json --output dashboard/index.html
python scripts/generate_report.py --input data/repo_status.example.json --output reports/daily_repo_report.md
```

## 目录结构

详见 `docs/index.md` 与 `docs/architecture.md`。

## Round 0 当前状态

- 当前轮：`round_00_bootstrap`
- 目标：建立项目骨架、治理协议、脚本骨架与静态 Dashboard
- 状态记录：`round_state/current_round.yaml`

## 后续路线

后续路线按 `docs/rounds/` 中 `round_01` 到 `round_10` 推进。

## 不做什么

- 不扫描全部 `~/PycharmProjects`
- 不读取密钥文件
- 不接真实 OpenClaw/Feishu/Telegram
- 不在 Round 0 做复杂前端框架化改造
