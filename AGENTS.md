# AGENTS.md

## 1) 项目身份

本项目为 `repo-ops-dashboard`，**个人多仓库管理总控台**。

核心价值：读取多个本地仓库的管理文件，汇总状态、判断优先级、识别卡点、生成报告与推进 Prompt，供 Cursor/Codex 执行、OpenClaw 调度、Human 决策。

## 2) 不是什么

本项目**不是**：

- 第三个编程 Agent
- 自动改所有仓库的机器人
- 自动提交器
- 自动删除器
- 全盘扫描器
- 密钥管理器

## 3) Agent 分工

### CursorAgent

负责：

- 本项目脚本实现
- Dashboard UI
- Playwright 本地 UI 检查
- 文档维护
- 本项目内部治理

### CodexAgent

负责：

- 边界清楚的批量推进
- 测试修复
- 自动 PR 或提交建议
- **不直接碰被管理业务仓库**

### OpenClawAgent

负责：

- 读取 `repo_status.json`
- 读取 `reports/`
- 触发只读扫描脚本
- 生成今日建议
- 生成 Cursor/Codex Prompt
- 推送提醒
- **不做主力编程开发**

### HumanOwner

负责：

- 决定优先级
- 决定冻结
- 决定归档
- 决定是否推进

## 4) 绝对禁止

- 禁止读取任何 `.env`
- 禁止打印任何 API Key
- 禁止修改被管理的业务仓库
- 禁止全量递归扫描所有仓库
- 禁止自动删除仓库
- 禁止自动 git commit
- 禁止自动接入通知平台
- 禁止在 Round 0 / Round 1 调用外部 API

## 5) Round 执行协议

每一轮必须：

1. 读取 `repo_protocol_standard.yaml`
2. 读取 `round_state/current_round.yaml`
3. 读取对应 `docs/rounds/round_xx_*.md`
4. 先输出计划
5. 再执行有限范围修改
6. 运行验证命令
7. 更新 `CHANGELOG.md`
8. 更新 `round_state/`
9. 生成 `reports/round_xx_completion_report.md`

## 6) Playwright 使用规则

- Playwright **只用于本地 Dashboard 页面检查**（`file://` 打开 `dashboard/index.html`）
- **不登录**任何真实网站
- **不读取**浏览器账号
- **不保存**敏感截图
- 截图只保存到 `reports/ui_screenshots/`
- Playwright 失败**不能影响**核心扫描脚本
- 未安装 Playwright 时，`ui_check.py` 应给出清晰安装提示并优雅退出

## 7) 验证命令

```bash
python3 scripts/agent_gate.py
python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/generate_dashboard.py --input data/repo_status.example.json --output dashboard/index.html
python3 scripts/generate_report.py --input data/repo_status.example.json --output reports/daily_repo_report.md
python3 scripts/ui_check.py --file dashboard/index.html --screenshot reports/ui_screenshots/dashboard.png --headless true
```

若 Playwright 未安装：

```bash
pip install -r requirements-dev.txt
python3 -m playwright install chromium
```

若命令因示例数据不足无法完整运行，必须在当轮完成报告说明原因与修复计划。
