# CHANGELOG

## Round 06 - Scheduler and Reports

- 确认 `generate_report.py` 日报/周报链路可用。
- 新增 `docs/scheduler.md` 本地 cron/launchd 调度说明。

## Round 08 - Feishu Notifications

- 新增 `scripts/prepare_feishu_payload.py`：本地 Feishu 载荷预览，路径脱敏，不发送 API。
- 更新 `docs/feishu_integration_plan.md` 人工确认流程。

## Round 07 - OpenClaw Bridge

- 更新 `skills/openclaw_repo_ops/SKILL.md`：只读接口、可触发命令、调度流程、硬边界。
- 新增 `prompts/openclaw_daily_brief.md` 每日简报模板。

## Round 05 - Prompt Generator

- 新增 `scripts/generate_prompts.py`：从 `repo_status.json` 生成 Cursor/Codex/OpenClaw 三类 Prompt。
- 模板变量化：`prompts/cursor_next_round.md`、`codex_next_round.md`、`openclaw_repo_scan.md` 支持 `{{repo_name}}` 等占位符。
- 输出目录 `prompts/generated/`（生成文件 gitignore，保留 `.gitkeep`）。

## Round 04 - Dashboard UI

- Dashboard 增加优先级/生命周期/Agent 过滤（`dashboard/app.js`）。
- 每仓卡片增加「复制 Prompt」按钮与 `data-*` 过滤属性。
- `ui_check.py` 增加过滤器与复制按钮检查。
- 样式更新：`dashboard/style.css` 过滤器与按钮。

## Round 03 - Status Analyzer

- `analyze_repos.py` 区分 `blockers`（关键治理缺失）与 `warnings`（非阻断扫描告警）。
- 新增 `lifecycle_status`、`last_checked` 字段；warning 数量影响 health_score。
- 更新 `docs/repo_status_schema.md`。

## Round 02 - Readonly Scanner

- `scan_repos.py` 输出结构化 `missing` / `skipped` / `warnings` 字段。
- 新增 `--max-file-kb` 大文件跳过（默认 512KB）。
- 重新生成 `data/repo_snapshots.example.json` 以匹配新 schema。
- 创建 `.venv` 并安装 Playwright Chromium（本地 UI 检查可用）。

## Round 1 - Independent Governance Audit & Playwright Preparation

- 独立审计上一轮 Agent 产物，生成 `reports/round_01_independent_audit_report.md`。
- 明确 repo-ops-dashboard 是多仓库编排总控台，不是编程 Agent。
- 强化 `AGENTS.md` 与 `repo_protocol_standard.yaml`（v0.2.0）。
- 新增 Playwright 开发依赖、`docs/playwright_setup.md` 与 `scripts/ui_check.py`。
- 扩写后续 Round 文档从 Round 00 到 Round 15。
- 改进被管理仓库扫描的安全边界说明。
- 增强 `agent_gate.py` 检查项（round 文档、Playwright 本地约束等）。
- Dashboard 轻量增强：archive 统计、lifecycle_status、last_checked。
- 为后续 OpenClaw 编排接入做准备（本轮未实际接入）。

## Round 0 - Bootstrap

- 创建 `repo-ops-dashboard` 项目骨架。
- 新增通用仓库治理协议文件。
- 新增 `AGENTS.md` 作为 agent 执行规则入口。
- 新增 Cursor 项目规则。
- 新增只读扫描与分析架构脚本骨架。
- 新增静态 Dashboard 骨架。
- 新增后续 Round 路线图文档。
- 新增 OpenClaw 接入规划文档。
- 新增 Feishu 与通知规划文档。
