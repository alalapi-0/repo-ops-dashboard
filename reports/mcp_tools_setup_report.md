# MCP 工具安装与自动运行配置 — 完成报告

**日期**：2026-06-02  
**分支**：main

## 已配置的 MCP

| Server | 状态 |
|--------|------|
| playwright | 保留（已有） |
| chrome-devtools | 保留（已有） |
| context7 | 保留（已有） |
| filesystem | 新增（`@modelcontextprotocol/server-filesystem`，授权 `.` = 工作区根） |
| github | 新增（`@modelcontextprotocol/server-github`，`${env:GITHUB_TOKEN}`） |

## 验证

| 命令 | 结果 |
|------|------|
| `python3 -m json.tool .cursor/mcp.json` | PASS |
| `python3 scripts/check_mcp_config.py` | PASS（filesystem `.` 警告为预期） |
| `python3 scripts/agent_gate.py` | WARNING（`protocol_round1_api` 既有项，非本轮引入） |
| `pytest` | 跳过（当前 shell 未激活 venv，无 pytest 模块） |

## Cursor 重启

修改 `.cursor/mcp.json` 后需 **完全退出并重启 Cursor**，再在 Tools & MCP 面板确认连接。

## GitHub Token

本地未配置 `GITHUB_TOKEN` 时不阻塞；Agent 使用 `git`/`gh` 降级。
