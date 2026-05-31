# Agent 浏览器验证闭环

本文档说明本仓库为 Cursor Agent 配置的浏览器调试与验证工具，以及如何使用与维护。

## 新增 MCP 服务器

以下 MCP 已写入 `.cursor/mcp.json`（项目级配置，可提交 GitHub）：

| MCP 名称 | 用途 |
|----------|------|
| **playwright** | 浏览器自动化：打开页面、点击、输入、截图、基本页面交互 |
| **chrome-devtools** | 深层 DevTools 调试：console、network、performance、DOM 检查 |
| **context7** | 查询最新库/框架文档；prompt 中可写 `use context7` |

### 各 MCP 说明

- **Playwright MCP**（`@playwright/mcp`）：适合普通用户路径验证、页面 snapshot、自动化操作。
- **Chrome DevTools MCP**（`chrome-devtools-mcp`）：适合检查 console error、network 失败、性能问题。
- **Context7 MCP**（`@upstash/context7-mcp`）：在修改依赖某框架/API 的代码前，先查最新文档，避免过时用法。

## 在 Cursor 中确认 MCP 已启用

1. 打开 **Cursor Settings**（macOS：`Cmd + ,`）。
2. 进入 **Tools & MCP** 或 **MCP** 面板。
3. 确认以下 server 为可用（绿色/Connected）状态：
   - `playwright`
   - `chrome-devtools`
   - `context7`
4. 若显示错误或 Pending，检查本机是否已安装 **Node.js v18+** 且 `npx` 可用。

## 修改配置后需重启 Cursor

`.cursor/mcp.json` 变更后，请**完全重启 Cursor**（Quit 后重新打开），再检查 MCP 状态。

## Prompt 示例

验证 Dashboard 或静态页面改动：

```
请调用 /browser-debug-check 技能完成本轮验证。
使用 Playwright MCP 打开 dashboard/index.html（file://），检查 console 无 error。
```

查最新文档后再改代码：

```
use context7 查询 Playwright Python API 最新用法，然后修复 ui_check.py。
```

本仓库 Python 侧已有 Playwright UI 检查（见 `docs/playwright_setup.md`）：

```bash
python3 scripts/ui_check.py \
  --file dashboard/index.html \
  --screenshot reports/ui_screenshots/dashboard.png \
  --headless true
```

Agent 门禁验证（Python 项目主验证入口）：

```bash
python3 scripts/agent_gate.py
```

## 配套 Skill 与 Rule

- **Skill**：`.cursor/skills/browser-debug-check/SKILL.md` — 完整浏览器验证流程与输出格式。
- **Rule**：`.cursor/rules/verification-gate.mdc` — 涉及前端/UI/API 的任务必须走验证闭环（`alwaysApply: true`）。

## 本仓库特殊说明

`repo-ops-dashboard` 是 **Python 多仓库总控台**，不是典型 Node 前端项目：

- 无根目录 `package.json`；Dashboard 为静态 `dashboard/index.html`。
- Playwright 通过 **Python**（`requirements-dev.txt` + `scripts/ui_check.py`）做本地 `file://` 检查，见 `AGENTS.md`。
- 未安装 `@playwright/test` smoke spec；如需 Node 侧 smoke test，需先引入前端构建链。

### MCP 浏览器与 `file://` 限制

Cursor 内置 **Playwright MCP** 与 **cursor-ide-browser** 均**禁止**直接打开 `file://` URL。Agent 验证 Dashboard 时请二选一：

1. **推荐（Python）**：`python3 scripts/ui_check.py --file dashboard/index.html ...`（原生支持 `file://`）。
2. **MCP 路径**：先启动本地 HTTP 服务，再用 `http://127.0.0.1:<port>/dashboard/index.html` 打开：

```bash
python3 -m http.server 8765 --bind 127.0.0.1
# MCP navigate → http://127.0.0.1:8765/dashboard/index.html
```

## 安全注意事项

- **不要**让 MCP 打开真实支付后台、生产管理后台或含隐私数据的页面。
- **不要**让 MCP 操作生产账号或真实用户 session。
- **不要**把 API Key、cookie、token、session 写入仓库或 MCP 配置。
- 测试删除/移动文件时，**必须**使用测试目录或测试数据。
- Playwright 在本项目仅用于本地 Dashboard（`file://`），**不登录**外网、**不访问**真实业务系统（见 `AGENTS.md`）。

## 相关文档

- [AGENTS.md](../AGENTS.md) — Agent 分工与 Playwright 边界
- [playwright_setup.md](./playwright_setup.md) — Python Playwright 安装与 `ui_check.py`
- [security_policy.md](./security_policy.md) — 安全策略
