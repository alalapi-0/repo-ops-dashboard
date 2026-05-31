# CHANGELOG

## Round 24 - Personal OS Hub

- 新增 `dashboard/hub.html` 统一入口页。
- Phase D 路线图标记完成。

## Round 23 - Feishu Hardening

- `prepare_feishu_payload.py`：20KB 截断、错误码提示、LLM 摘要段落、签名单测。
- 飞书/Automation 文档：限流、关键词、IP 白名单说明。

## Round 22 - OpenRouter LLM Summary

- 新增 `scripts/generate_llm_summary.py`（dry-run 默认，`--call` opt-in）。
- `refresh_status.sh --llm-summary [--call]`；`.env.example` OpenRouter 变量。

## Round 21 - Daily Brief Rename & Cursor Orchestration

- `generate_openclaw_brief.py` → `generate_daily_brief.py`；prompts/reports 同步重命名。
- 新增 `docs/cursor_automation_guide.md`；OpenClaw Skill 标记 deprecated。
- `generate_prompts.py` 使用 `orchestration` 模板键。

## Round 20 - Environment Template

- 修复 `.gitignore` 放行 `.env.example`。
- 扩展 OpenRouter + Feishu 环境变量模板；新增 `docs/env_configuration.md`。

## Round 19 - Local Imports Optional

- 新增 `scripts/read_local_imports.py`：从 `config/local_imports.yaml` 只读 ICS/CSV 摘要。
- 示例数据 `data/sample_calendar.example.ics`、`data/sample_finance.example.csv`；并入 weekly_review。
- **Phase C 全部完成**。

## Round 18 - Weekly Review & Human Notes

- 新增 `scripts/generate_weekly_review.py`：合并 priority_review、OpenClaw brief、weekly report 与 human notes。
- 新增 `data/human_notes.example.json`；Dashboard 展示「本周 Human 笔记」区块。
- `ui_check.py` 增加 human_notes 检查；`refresh_status.sh` 链路重排。

## Round 17 - Feishu Bitable Sync

- 新增 `scripts/sync_feishu_bitable.py`：从 `repo_status.json` 幂等 upsert 飞书多维表格（dry-run 默认，`--sync` opt-in，stdlib API）。
- 新增 `docs/feishu_bitable_schema.md` 字段与 Human 配置说明。
- `refresh_status.sh` 增加 `--bitable-sync`；`.env.example` 扩展 Bitable 凭证占位。
- 新增 `tests/test_feishu_integration.py`。

## Round 16 - Cursor Automations Feishu Push

- `refresh_status.sh` 增加 `--feishu-send`；OpenClaw brief 先于 Feishu 预览生成。
- 增强 `prepare_feishu_payload.py`：概览统计、OpenClaw 摘要、`--status` / `--brief` 参数。
- 新增 `docs/cursor_automation_feishu.md` 与 Round 16/17 文档。
- 更新 `feishu_integration_plan.md`、`downstream_integrations.md`、`scheduler.md`。

## Round 15 - Personal OS Roadmap

- 新增 `docs/personal_os_roadmap.md`：个人 OS 远期规划（文档 only，Round 00–15 完结）。

## Round 14 - OpenClaw Daily Briefing

- 新增 `scripts/generate_openclaw_brief.py`：规则生成每日简报（推进/暂缓/风险/任务/短提醒）。
- 更新 `skills/openclaw_repo_ops/SKILL.md` 与 `refresh_status.sh`。

## Round 13 - Cross-Repo Protocol Sync

- 新增 `scripts/protocol_sync_report.py`：只读对比治理文件差异，生成 `reports/protocol_sync_suggestions.md` 与 `prompts/generated/*_protocol_sync.md`。
- 新增 `prompts/protocol_sync_cursor.md` 模板；`refresh_status.sh` 纳入协议同步步骤。

## Round 12 - Priority Review System

- 新增 `config/priority_factors.yaml` 与 `scripts/priority_review.py`：多因素建议优先级，Human 可通过 `priority_hint` 覆盖。
- Dashboard 卡片展示「优先级来源」（算法建议 / 人工覆盖）。
- `refresh_status.sh` 链路加入 priority_review；新增 `tests/test_priority_review.py`。

## Round 10 - Release Hardening

- 新增 `tests/`（analyze、agent_gate、priority_review）与 `pytest.ini`。
- 新增 `scripts/refresh_status.sh`：一条命令刷新 gate → scan → analyze → priority → dashboard → report → feishu 预览 → ui_check。
- `agent_gate.py` 增加 installation.md、example fixtures、pytest 存在性检查。
- 完善 `docs/installation.md`。

## Registry, Lifecycle & Downstream Integrations

- 新增 `config/repos.yaml`：登记 `/Users/alalapi/PycharmProjects` 下 17 个项目。
- 新增 `scripts/sync_repo_registry.py`：合并新子目录，不覆盖已有 `priority_hint`。
- `scan_repos.py`：`empty` 状态；`analyze_repos.py`：`missing`/`empty` → `archive_candidate` / `archived`。
- 新增 `docs/lifecycle_rules.md`、`docs/downstream_integrations.md`、`docs/installation.md`。
- `prepare_feishu_payload.py`：实现 `--send`（urllib + 可选 `FEISHU_SIGN_SECRET`）。
- 更新调度/通知/OpenClaw 文档为多下游可选路线；`repos.example.yaml` 移除 `old_demo_placeholder`。

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
