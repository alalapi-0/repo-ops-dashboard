# Round 00 - Bootstrap

## 目标

- 创建仓库骨架与治理协议
- 创建 `AGENTS.md`、Cursor Rules、基础脚本
- 创建静态 Dashboard 示例与 Round 路线图
- 建立安全边界与 Agent 分工文档

## 不做什么

- 不接 OpenClaw/Feishu 实际 API
- 不修改被管理业务仓库
- 不全量扫描业务仓源码
- 不创建真实 `config/repos.yaml`

## 前置条件

- 本地 Python 3.10+ 环境
- 空仓库或最小 git 初始化

## 输入文件

- 用户提供的项目定位与安全约束
- `repo_protocol_standard.yaml`（初版）

## 输出文件

- `scripts/*.py`（scan/analyze/dashboard/report/agent_gate）
- `dashboard/*`
- `docs/rounds/*`（初版）
- `round_state/current_round.yaml`
- `reports/round_00_completion_report.md`

## 阶段任务

### 阶段 1 — 骨架初始化

- 创建目录结构：config、scripts、dashboard、docs、data、reports、round_state
- 创建 `.gitignore` 排除密钥与本地数据

### 阶段 2 — 治理文件落地

- 编写 `AGENTS.md`、`README.md`、`repo_protocol_standard.yaml`
- 创建 `.cursor/rules/repo_ops_dashboard.mdc`

### 阶段 3 — 脚本与示例数据

- 实现只读扫描、分析、Dashboard 生成、报告生成
- 提供 `*.example.json` 与 `repos.example.yaml`

### 阶段 4 — 验证与收尾

- 运行验证命令链
- 更新 CHANGELOG 与 round_state

## 验收标准

- 核心结构完整，5 个脚本可运行
- 指定验证命令可执行或有明确失败说明
- 无密钥读取、无外部 API、无业务仓写入
- Round 00 完成报告存在

## 已完成 / 未完成

**已完成：** 骨架、协议、5 脚本、静态 Dashboard、Round 00–10 初版文档、OpenClaw/Feishu 规划文档。

**未完成：** 真实 `repos.yaml`、Playwright UI 检查、Round 11–15、OpenClaw/Feishu 实际接入。

## 风险点

- 示例数据与真实仓库状态可能偏差
- 规则初版需后续轮次细化

## 推荐执行 Agent

- Cursor

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
Round 00 已完成。请从 Round 01 治理复核或 Round 02 只读扫描继续。
验证：python3 scripts/agent_gate.py && python3 scripts/scan_repos.py --dry-run
```
