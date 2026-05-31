# Round 07 - OpenClaw Bridge

## 目标

- 让 OpenClaw 读取 `repo_status.json`
- 让 OpenClaw 触发只读扫描脚本
- 让 OpenClaw 输出今日建议
- 让 OpenClaw 生成提醒文本
- **不让** OpenClaw 直接修改业务仓库

## 不做什么

- 不接 OpenClaw SDK（本轮仅文档与 Skill）
- 不让 OpenClaw 写被管理仓库
- 不让 OpenClaw 主力编程

## 前置条件

- 扫描/分析/报告脚本稳定
- `skills/openclaw_repo_ops/SKILL.md` 存在

## 输入文件

- `data/repo_status.json`
- `reports/daily_repo_report.md`
- `skills/openclaw_repo_ops/SKILL.md`

## 输出文件

- 更新的 OpenClaw Skill 文档
- `prompts/openclaw_daily_brief.md`（模板）

## 阶段任务

### 阶段 1 — 只读接口定义

- 文档列出 OpenClaw 可读取的文件路径
- 文档列出可触发的 shell 命令（dry-run 默认）

### 阶段 2 — Skill 更新

- 更新 SKILL.md：调度流程、边界、示例命令

### 阶段 3 — 提醒文本模板

- 今日最该推进的 1–3 仓
- 今日不该碰的仓

## 验收标准

- Skill 文档清晰可执行
- 所有命令默认 dry-run 或只读
- 无业务仓写入路径

## 风险点

- OpenClaw 误读为编程 Agent
- 需 Human 确认触发写操作

## 推荐执行 Agent

- Cursor（文档）/ Human（OpenClaw 配置）

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
更新 openclaw_repo_ops Skill：只读读 status/report，触发 scan --dry-run。
禁止修改被管理仓库。生成今日建议 Markdown 模板。
```
