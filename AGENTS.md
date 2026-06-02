# AGENTS.md

## 1) 项目身份

本项目为 `repo-ops-dashboard`，是用户个人多仓库治理层 / Personal Agent OS / Portfolio Orchestrator。

它负责在“一个人 + 多个 AI Agent + 多个仓库/项目”的条件下，登记项目、汇总状态、判断优先级、生成 task_spec、组织 handoff、收集 proof_of_work、维护 review_queue，并为 HumanOwner 提供可审计的决策材料。

它不是普通 Dashboard。Dashboard 只是治理状态的一个视图。

## 2) 不是什么

本项目不是：

- Cursor/Codex 替代品
- 领域 Agent
- 全自动无人值守系统
- 直接修改所有仓库的工具
- 密钥读取工具
- 发布工具
- 自动删除器
- 自动提交器
- 全盘扫描器

## 3) Agent 分工

### CursorAgent

负责：

- 本项目功能开发
- 脚本实现
- Dashboard UI
- Playwright 检查
- 文档维护
- Round 执行
- 本项目内部治理资产维护

### CodexAgent

负责：

- 边界清楚的批量推进
- 明确任务实现
- 测试修复
- PR/提交建议
- 不直接碰被管理业务仓库，除非 HumanOwner 在独立业务仓库内明确授权

### OpenClawAgent

负责：

- 调度入口
- 读取 `repo_status`、`portfolio_state`、`weekly_digest`、`review_queue`
- 生成今日建议
- 触发只读脚本
- 生成 Cursor/Codex Prompt
- 提醒 HumanOwner 处理 HITL 决策
- 不做主力编程开发

### HumanOwner

负责：

- 优先级
- 预算
- 冻结/归档/删除
- 发布
- 规则写入
- 高风险确认
- 破例通过未达标任务

## 4) 每轮执行协议

每轮必须：

1. 读取 `repo_protocol_standard.yaml`
2. 读取 `round_state/current_round.yaml`
3. 读取对应 `docs/rounds` 文档或路线映射
4. 输出计划
5. 限定范围执行
6. 运行验证命令
7. 更新 `CHANGELOG.md`
8. 更新 `round_state/`
9. 生成 completion report
10. 如有任务完成，生成或规划 `proof_of_work`

## 5) 任务与验收协议

每个治理任务必须有：`task_id`、`project_id`、目标、范围、`working_directory`、`assigned_agent`、验收标准、验证命令、proof_of_work、blockers、状态和时间戳。

完成不能靠“感觉完成了”，必须提交 proof_of_work 或在 completion report 中说明为什么暂未生成。

## 6) 绝对禁止

- 禁止读取任何 `.env`
- 禁止打印任何 API Key、Token、密码、私钥
- 禁止修改被管理业务仓库
- 禁止全量递归扫描所有仓库
- 禁止自动删除项目或仓库
- 禁止自动 git commit/push
- 禁止自动接通知平台
- 禁止自动发布
- 禁止自动改 reference_lab
- 禁止绕过 review_queue
- 禁止在治理轮调用外部大模型 API

## 7) Playwright 使用规则

- Playwright 只用于本地 Dashboard 页面检查（`file://` 打开 `dashboard/index.html`）
- 不登录任何真实网站
- 不读取浏览器账号
- 不保存敏感截图
- 截图只保存到 `reports/ui_screenshots/`
- Playwright 失败不能影响核心扫描脚本，但必须写入报告
- 未安装 Playwright 时，`ui_check.py` 应给出清晰安装提示并优雅退出

## 8) MCP Tools

当前项目要求启用以下 **Workspace MCP Servers**（见 `.cursor/mcp.json`）：

- **chrome-devtools**：浏览器调试、console、network、页面状态检查。
- **context7**：查询第三方库和框架文档。
- **filesystem**：安全读取和检查当前项目文件（仅授权工作区根目录）。
- **github**：仓库、提交、分支、issue、PR 等相关操作（token 通过环境变量，勿写入仓库）。
- **playwright**：浏览器自动化、页面操作、E2E 检查。

**自动推进轮开始前**，Agent 必须确认上述 MCP 已加载（`npm run check:mcp` 或 `node scripts/check_mcp_config.js`）。若某个 MCP 不可用，须记录原因并使用可用替代方案继续推进（见 `docs/agent_skills/mcp_usage_skill.md`）。

涉及页面、审核台、生成结果、预览、发布流程的任务，**必须**使用 chrome-devtools 或 playwright 进行真实浏览器检查。

修改 `.cursor/mcp.json` 后需**完全退出并重启 Cursor** 才能在 Tools & MCP 面板生效。

## 9) 验证命令

```bash
npm run check:mcp
python3 scripts/agent_gate.py
python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/generate_dashboard.py --input data/repo_status.example.json --output dashboard/index.html
python3 scripts/generate_report.py --input data/repo_status.example.json --output reports/daily_repo_report.md
python3 scripts/ui_check.py --file dashboard/index.html --screenshot reports/ui_screenshots/dashboard.png --headless true
```
