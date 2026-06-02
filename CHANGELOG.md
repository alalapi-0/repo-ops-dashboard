# CHANGELOG

## Round 51 - Project Rule Promotion

- 新增 `project_rule_promotion_policy.yaml` 与 `promote_project_rule.py`（默认不自动合并 review_queue）。
- 生成 `governance/project_rule_promotion_queue.yaml`；`refresh_status` 与 `agent_gate` 纳入推广验收。
- `reports/round_51_completion_report.md`。

## Round 50 - Skill / Playbook Candidate Extraction

- 新增 `playbook_extraction_policy.yaml` 与 `extract_playbook_candidates.py`。
- 生成 `governance/playbook_candidates.yaml`；`refresh_status` 与 `agent_gate` 纳入候选提取验收。
- `reports/round_50_completion_report.md`。

## Round 49 - Checkpoint Snapshot

- 新增 `checkpoint_snapshot_policy.yaml`、portfolio 快照脚本与 `governance/checkpoints/manifest.yaml`。
- `refresh_status.sh` 在 sync portfolio 后执行 checkpoint dry-run；`agent_gate` 增加 checkpoint 验收。
- `reports/round_49_completion_report.md`。

## Round 48 - Failure Recovery & Retry Policy

- 新增 `failure_recovery_policy.yaml`、planner/validator 脚本与设计文档。
- 定义 retry_count、failure_class、checkpoint_id 与 review_queue 升级规则。
- `refresh_status.sh`、`agent_gate` 与 eval registry 增加 failure_recovery 验收。
- `reports/round_48_completion_report.md`。

## Round 47 - Handoff Protocol Implementation

- 新增 handoff 模板、示例 packet、`tracking.yaml` 与 generate/validate 脚本。
- `refresh_status.sh`、`agent_gate` 与 eval registry 增加 handoff 验收项。
- `reports/round_47_completion_report.md`。

## Round 46 - Eval Registry Script

- 新增 `run_eval_registry.py` 与 `reports/eval_registry_run.md` 输出；registry 增加 runner 元数据。
- `completion_report_exists` 改为 round_state 动态解析；新增 `eval_registry_runner_valid` 验收项。
- `refresh_status.sh`、`tests/test_run_eval_registry.py` 与 `agent_gate` eval_registry_runner 检查。
- `reports/round_46_completion_report.md`。

## Round 45 - Daily Briefing MVP

- 新增 `generate_daily_briefing.py`、`prompts/daily_briefing.md` 与治理 digest 输出路径。
- `refresh_status.sh` 与 `tests/test_generate_daily_briefing.py`；`agent_gate` daily_briefing 检查。
- `reports/round_45_completion_report.md`。

## Round 44 - Weekly Digest MVP

- 新增 `generate_weekly_digest.py` 与 `governance/digests/weekly/weekly_digest.md`。
- `prompts/weekly_digest.md`、`tests/test_generate_weekly_digest.py`；`agent_gate` weekly_digest 检查。
- `reports/round_44_completion_report.md`。

## Round 43 - OpenClaw Orchestration Bridge

- 新增 `openclaw_orchestration_bridge.py`、`openclaw_orchestration.manifest.yaml` 与 orchestration brief 模板。
- 同步 `governance_task_queue.yaml`（2 task_spec）；更新 OpenClaw Skill 与集成规划。
- `tests/test_openclaw_orchestration_bridge.py`；`reports/round_43_completion_report.md`。

## Round 42 - Prompt Generator for Codex

- 新增 `generate_codex_prompt_from_task_spec.py`、`codex_from_task_spec.md` 与 `example_codex_task_spec.yaml`。
- `refresh_status.sh` 与 `tests/test_generate_codex_prompt_from_task_spec.py`。
- `reports/round_42_completion_report.md`。

## Round 41 - Prompt Generator for Cursor

- 新增 `generate_cursor_prompt_from_task_spec.py` 与 `prompts/cursor_from_task_spec.md`。
- `refresh_status.sh` dry-run 生成；`tests/test_generate_cursor_prompt_from_task_spec.py`。
- `reports/round_41_completion_report.md`。

## Round 40 - Playwright Dashboard Validation

- 新增 `config/ui_check_policy.yaml` 与 `validate_ui_check_policy.py`。
- `ui_check.py` 增强 console/network 监听、过滤器与复制按钮交互、`--url` HTTP 预览。
- `tests/test_ui_check.py`；`agent_gate` 与 eval registry 增加 ui_check_policy 验收。
- `reports/round_40_completion_report.md`。

## Round 39 - Dashboard V2

- `generate_dashboard.py` 新增治理面板 V2：portfolio_state、task_queue、review_queue、blockers。
- 更新 `dashboard/style.css` 与 `ui_check.py` 验收；`tests/test_generate_dashboard.py`。
- `reports/round_39_completion_report.md`。

## Round 38 - Blocker Management

- 新增 `config/blocker_policy.yaml` 与三类 blocker（governance_missing / repository_path / repository_empty）。
- 新增 `scripts/blocker_management.py` 实现分类与超时升级（info→warning→review→hitl）。
- `analyze_repos.py` 输出 `blocker_details`；`agent_gate` 与 eval registry 增加 blocker_policy 验收。
- `reports/round_38_completion_report.md`。

## Round 37 - Lifecycle Rules

- 新增 `config/lifecycle_policy.yaml` 与八态生命周期（idea/bootstrap/active/blocked/maintenance/frozen/archived/abandoned）。
- `analyze_repos.py` 默认经 `derive_lifecycle_v1` 映射 `lifecycle_status`；更新 `docs/lifecycle_rules.md`。
- `agent_gate` 与 eval registry 增加 lifecycle_policy 验收；`reports/round_37_completion_report.md`。

## Round 36 - Priority Scoring System

- 新增 `config/priority_scoring_policy.yaml` 与治理示例；`scripts/priority_scoring.py` 实现 impact×urgency×unblock−cost−risk。
- `analyze_repos.py` 输出 `priority_score` 字段；Dashboard 与 `portfolio_state` 同步展示。
- `agent_gate` 与 eval registry 增加 priority_scoring 验收；`reports/round_36_completion_report.md`。

## Round 35 - Status Analyzer V2

- 新增 `config/analyzer_policy.yaml` 与 `governance/analyzer_policy.example.yaml`（registry/snapshot/round_state 健康维度）。
- 新增 `scripts/validate_analyzer_policy.py`、`read_analyzer_policy.py`；`analyze_repos.py` 输出 v2 字段。
- `agent_gate` 与 eval registry 增加 analyzer_policy 验收；扩展 `tests/test_analyze_repos.py` 与 `reports/round_35_completion_report.md`。

## Round 34 - Readonly Repo Scanner V2

- 新增 `config/scan_policy.yaml` 与 `governance/scan_policy.example.yaml`（核心治理分类 readme/agents/protocol/round_state）。
- 新增 `scripts/validate_scan_policy.py`、`read_scan_policy.py`；`scan_repos.py` 输出 v2 字段。
- `agent_gate` 与 eval registry 增加 scan_policy 验收；新增 `tests/test_scan_repos.py` 与 `reports/round_34_completion_report.md`。

## Round 33 - Repo Context Index MVP

- 新增本仓库 `repo_context_index.yaml` 与 `governance/repo_context_index.example.yaml`。
- 新增 `scripts/validate_repo_context_index.py`、`read_repo_context_index.py`、`build_repo_context_index_stub.py`。
- `agent_gate` 与 eval registry 增加 repo_context_index 验收；扫描 allowlist 纳入 `repo_context_index.yaml`。
- 新增 `tests/test_repo_context_index.py` 与 `reports/round_33_completion_report.md`。

## Round 32 - Execpolicy Checker

- 新增 `scripts/validate_execpolicy.py`、`read_execpolicy.py`、`check_execpolicy_action.py`。
- `agent_gate` 与 eval registry 增加 execpolicy 验收。
- 新增 `tests/test_execpolicy.py` 与 `reports/round_32_completion_report.md`。

## Round 31 - Review Queue MVP

- 新增 `scripts/validate_review_queue.py`、`read_review_queue.py`、`add_review_queue_item.py`、`close_review_queue_item.py` 与 `review_queue.example.yaml`。
- `agent_gate` 与 eval registry 增加 review_queue 验收。
- 新增 `tests/test_review_queue.py` 与 `reports/round_31_completion_report.md`。

## Round 30 - Agent Run JSONL Audit Trail

- 新增 `scripts/validate_agent_run.py`、`read_agent_run.py`、`record_agent_run_event.py` 与 `governance/runs/example_run.jsonl`。
- `agent_gate` 与 eval registry 增加 agent_run JSONL 验收。
- 新增 `tests/test_agent_run_jsonl.py` 与 `reports/round_30_completion_report.md`。

## Round 29 - Proof of Work System

- 新增 `scripts/validate_proof_of_work.py`、`read_proof_of_work.py`、`sync_proof_of_work_registry.py` 与 `governance/proof_of_work_registry.yaml`。
- `agent_gate` 与 eval registry 增加 proof_of_work_registry 验收。
- 新增 `tests/test_proof_of_work_registry.py` 与 `reports/round_29_completion_report.md`。

## Round 28 - Governance Task Queue

- 新增 `scripts/sync_governance_task_queue.py`、`scripts/read_task_spec.py` 与 `governance/governance_task_queue.yaml`。
- `agent_gate` 与 eval registry 增加 governance_task_queue 验收。
- 新增 `tests/test_governance_task_queue.py` 与 `reports/round_28_completion_report.md`。

## Round 27 - Portfolio State Snapshot

- 新增 `scripts/sync_portfolio_state.py` 与 `governance/portfolio_state.yaml`（registry + repo status 合并快照）。
- `agent_gate` 与 eval registry 增加 portfolio_state 验收。

## Round 26 - Project Registry MVP

- 新增 `scripts/sync_project_registry.py` 与 `governance/project_registry.yaml`（从 `config/repos.yaml` 同步 17 个项目）。
- `agent_gate` 增加 project_registry 校验；eval registry 增加 `project_registry_exists`。
- 新增 `tests/test_project_registry.py` 与 `reports/round_26_completion_report.md`。

## Round 25 - Personal Agent OS Architecture Absorption

- 将项目定位升级为个人多仓库治理层 / Personal Agent OS / Portfolio Orchestrator。
- 新增 `governance/` 治理资产目录、task_spec、proof_of_work、review_queue、execpolicy 与 eval registry。
- 新增数据模型、参考架构吸收、审计轨迹、handoff、review_queue、execpolicy、repo_context_index、evaluation gate 设计文档。
- 新增 `docs/roadmap_40_rounds.md`，并将架构路线映射到仓库执行 Round 25-63。
- 增强 `scripts/agent_gate.py` 的治理资产检查。

## MCP 工具配置轮

- 合并 `.cursor/mcp.json`：补充 filesystem、github（保留 playwright / chrome-devtools / context7）。
- 新增 `docs/agent_skills/mcp_usage_skill.md`、`scripts/check_mcp_config.py`、`.cursor/rules/mcp-agent-tools.mdc`。
- 更新 `AGENTS.md`、`README.md`、`docs/agent-browser-verification.md`。

## Autonomous Round 1 - Agent Verification

- 执行 agent_gate、pytest（37）、ui_check、MCP 浏览器验证（经本地 HTTP）。
- 真实 OpenRouter 调用返回 401（密钥需 Human 更新）；文档补充 MCP `file://` 限制说明。

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
