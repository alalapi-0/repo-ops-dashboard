# MCP 使用技能（Agent 自动推进轮）

本文档说明 `repo-ops-dashboard` 在 Cursor / Agent 工作流中启用的 MCP 工具、授权范围与降级策略。配置源文件：`.cursor/mcp.json`。

## 1. 当前启用的 MCP

| Server 名称 | 包 / 命令 | 用途 |
|-------------|-----------|------|
| **playwright** | `@playwright/mcp` | 浏览器自动化：打开页面、点击、输入、截图、snapshot、基础 E2E 验收 |
| **chrome-devtools** | `chrome-devtools-mcp` | DevTools 级检查：console、network、performance、DOM |
| **context7** | `@upstash/context7-mcp` | 查询库/框架最新文档（prompt 中可写 `use context7`） |
| **filesystem** | `@modelcontextprotocol/server-filesystem` | 在授权目录内稳定读写、列举项目文件 |
| **github** | `@modelcontextprotocol/server-github` | 读取仓库、提交、issue、PR 等（需 token 时降级） |

已有 server **不得**在合并配置时被删除；新增项仅做补充。

## 2. Playwright MCP

- **用于**：Dashboard / 静态页 UI 验收、用户路径点击、页面 snapshot、与 `browser-debug-check` Skill 配合。
- **限制**：Cursor 侧 Playwright MCP **通常禁止**直接 `file://`；本仓库 Dashboard 验证优先 `python3 scripts/ui_check.py`，或先 `python3 -m http.server` 再用 MCP 打开 `http://127.0.0.1:<port>/dashboard/index.html`（见 `docs/agent-browser-verification.md`）。
- **禁止**：登录外网真实账号、访问生产后台、保存含隐私的截图到仓库外路径。

## 3. 文件系统 MCP 授权范围

- 配置参数为工作区相对路径 `"."`（Cursor 从**本项目根目录**启动 MCP 时，仅允许当前仓库树）。
- **禁止**将 filesystem 授权为 `/`、`C:\`、用户主目录根路径或整个磁盘。
- Agent 写入/删除前必须用 git diff 或读文件确认真实状态，不得假设磁盘内容。

若需在其他机器上改为绝对路径，由 Human 本地修改 `.cursor/mcp.json` 的 `filesystem.args` 最后一项为**仅此仓库**的绝对路径，且勿提交个人路径到 Git（可用本地 gitignore 覆盖或仅文档说明）。

## 4. GitHub MCP 与 Token

- 官方 server 读取环境变量 **`GITHUB_PERSONAL_ACCESS_TOKEN`**。
- 项目配置通过 `${env:GITHUB_TOKEN}` 映射（在 shell / Cursor 环境变量中设置 `GITHUB_TOKEN`，**勿**写入仓库）。
- **无 token 时**：GitHub MCP 可能无法连接；Agent 应改用 `git` / `gh` CLI 只读操作，并记录原因，**不阻塞**整轮推进（除非任务唯一依赖 GitHub API）。

## 5. 文档查询 MCP（Context7）

- 已启用 **context7**；修改依赖外部库/框架的代码前，优先查文档再改实现。
- 无 API Key 时 Context7 通常仍可对公开文档查询；若不可用，降级为项目内 `docs/`、`README.md` 与官方站点链接。

## 6. 无 API Key / Token 时的降级

| 能力 | 降级方式 |
|------|----------|
| GitHub MCP | `git log` / `git status` / `gh`（若已登录） |
| Playwright MCP | `scripts/ui_check.py`（Python Playwright） |
| Chrome DevTools MCP | `ui_check.py` + 人工查看 |
| Context7 | 本地 `docs/`、框架官方文档 |
| Filesystem MCP | Cursor 内置读写在授权范围内的文件工具 |

自动推进轮进入 **mock / dry-run** 时，须在 completion report 中写明缺失项与替代路径。

## 7. 后续自动推进轮如何使用 MCP

1. 轮次开始前运行：`python3 scripts/check_mcp_config.py`（或 `python3 scripts/agent_gate.py` 后执行）。
2. 在 Cursor **Tools & MCP** 确认 server 已连接；若未加载，按本文档与 `docs/agent-browser-verification.md` 排查（Node 18+、`npx`、重启 Cursor）。
3. **UI / 前端 / Dashboard**：调用 `.cursor/skills/browser-debug-check/SKILL.md`；必须查看 **页面、console、network、核心流程**，不得仅凭代码 diff 宣布完成。
4. **改依赖/API**：`use context7` 或 Context7 MCP 查文档。
5. **仓库状态 / PR**：有 token 用 GitHub MCP；否则 git/gh + 文档记录。
6. **文件变更**：filesystem MCP 或内置工具 + `git diff` 提交前复核。

## 8. 安全红线

- **禁止**向 Git 提交 `.env`、cookie、session、API Key、token。
- **禁止**在 `.cursor/mcp.json` 或文档中写死真实密钥。
- **禁止** filesystem 授权系统根目录或用户主目录全盘。
- **禁止** MCP 打印或回显密钥（检查脚本亦不得输出 token 值）。

## 9. 修改配置后

- 变更 `.cursor/mcp.json` 后需 **完全退出并重启 Cursor**，再在 MCP 面板确认连接状态。
- 运行 `python3 scripts/check_mcp_config.py` 做静态校验。

## 10. 相关文件

- `.cursor/mcp.json` — MCP server 声明
- `.cursor/rules/mcp-agent-tools.mdc` — Agent 强制规则
- `.cursor/rules/verification-gate.mdc` — 验证闭环
- `docs/agent-browser-verification.md` — 浏览器验证与 `file://` 说明
- `AGENTS.md` — MCP Tools 章节
