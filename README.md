# Repo Ops Dashboard

个人多仓库管理总控台 / 仓库项目经理 / Repo Ops Dashboard。

## 项目定位

`repo-ops-dashboard` 是一个多仓库治理与调度层项目，用于读取多个本地仓库的管理文件，汇总状态并生成可执行推进建议。  
它不是业务产品，不是普通 Web 应用，**也不是第三个编程 Agent**。

## 长期目标

1. 管理多个本地仓库状态
2. 只读取每个仓库的管理文件
3. 汇总项目进度
4. 判断优先级
5. 识别卡住的仓库
6. 识别应冻结或归档的仓库
7. 生成每日/每周报告
8. 生成给 Cursor/Codex 的推进 Prompt
9. 可选下游：OpenClaw、Hermes、Cursor Automations 或本地推理服务（见 `docs/downstream_integrations.md`）
10. 可选 Feishu/Lark 推送（`prepare_feishu_payload.py --send`）或 Mac 通知

## 为什么它不是编程 Agent

- 本项目本身不承担主力编码执行角色
- 本项目只聚合状态、生成建议与下一轮提示词
- Cursor 和 Codex 仍然是主要编程执行工具
- OpenClaw 后续只作为调度入口和提醒入口，不负责主力代码开发

## Agent 分工

- **Cursor**：开发本项目、写脚本、调试 Dashboard、接 Playwright
- **Codex**：执行明确推进轮、批量修改、自动 PR
- **OpenClaw**：后续做调度、提醒、入口调用，**不承担主力开发**
- **Human**：决定优先级、冻结、归档与推进方向

## 安全边界

- 本项目不会直接修改被管理的业务仓库
- 本项目默认只读取仓库管理文件
- 本项目不读取 `.env`、密钥、Token、账号文件
- Round 0 / Round 1 不调用外部 API，不接真实通知平台
- Playwright 仅用于本地 Dashboard UI 检查，不登录任何网站

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # Playwright 开发依赖（可选）
python3 -m playwright install chromium   # 仅 UI 检查需要

python3 scripts/agent_gate.py
python3 scripts/scan_repos.py --config config/repos.yaml --dry-run
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/generate_dashboard.py --input data/repo_status.example.json --output dashboard/index.html
python3 scripts/generate_report.py --input data/repo_status.example.json --output reports/daily_repo_report.md
python3 scripts/ui_check.py --file dashboard/index.html --screenshot reports/ui_screenshots/dashboard.png --headless true
```

## 目录结构

详见 `docs/index.md` 与 `docs/architecture.md`。

## 当前状态

- 真实登记：[`config/repos.yaml`](config/repos.yaml)（17 个 PycharmProjects 项目）
- 状态记录：`round_state/current_round.yaml`
- 安装与日常运行：[`docs/installation.md`](docs/installation.md)

## 后续路线

按 `docs/rounds/` 中 `round_00` 到 `round_15` 推进；Round 01 登记与 Round 11 生命周期规则已落地。

## 不做什么

- 不递归扫描业务源码
- 不读取密钥文件
- 不自动删除被管理仓库
- 不在早期轮次做复杂前端框架化改造
