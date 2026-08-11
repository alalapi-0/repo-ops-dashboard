# MCP 分层状态与使用边界

本文档区分四类不同事实：

1. **候选/支持能力**：仓库文档或代码知道如何使用某类 server。
2. **当前宿主配置**：仅以 `.cursor/mcp.json` 当前内容为准。
3. **运行时状态**：是否已安装、启动、可达、健康和已认证，必须独立观测。
4. **动作权限**：每次读取、写入或外部效果都由当前用户和上层策略决定。

前三者都不能自行证明第四者。配置或 gate 结果也不能授权推进轮次、写日志、修改文件或执行 Git 操作。

## 候选能力

| Server | 用途 |
|---|---|
| `playwright` | 本地 Dashboard 交互验证 |
| `chrome-devtools` | console、network、DOM 诊断 |
| `context7` | 第三方库文档查询 |
| `filesystem` | 限定工作区内的文件操作 |
| `github` | GitHub 仓库、issue 和 PR 操作 |

这张表不声明它们已配置或可用。仓库不会自动补齐或恢复 `.cursor/mcp.json` 中缺失的候选项。

## 安全要求

- filesystem 不得授权 `/`、用户主目录、整个磁盘或多仓库父目录。
- 不得打印、记录或提交 API Key、token、cookie、session 或私钥。
- 不得用 MCP 登录外网真实账号、访问生产后台或修改用户数据。
- UI 验证优先使用 `scripts/ui_check.py`；仅在当前权限允许且工具已配置、已观测可用时才调用 MCP。
- GitHub 外部效果始终需要单独的当前权限；存在 server 或 token 引用不构成授权。

## 验证与诊断

`python3 scripts/check_mcp_config.py` 或 `npm run check:mcp` 只检查 JSON 结构、范围和明显的密钥风险。它们接受部分配置，不显示完整启动参数，不测试运行时，不写报告，也不授权后续动作。

若宿主所有者单独修改 `.cursor/mcp.json`，Cursor 可能需重启才重新发现配置。缺少候选能力时，只返回当前可证实的缺口；不自动安装、改配置、写 completion report 或推进任务。

## 相关文件

- `.cursor/mcp.json` — 当前宿主配置
- `.cursor/rules/mcp-agent-tools.mdc` — 已授权调用的安全限制
- `.cursor/rules/verification-gate.mdc` — 已授权变更的验证深度
- `docs/agent-browser-verification.md` — 本地浏览器验证
- `AGENTS.md` — 项目范围与上层权限边界
