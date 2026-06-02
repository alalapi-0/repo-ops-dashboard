# Round 25 架构吸收审计报告

## 1. 当前仓库结构

`repo-ops-dashboard` 已具备一个轻量多仓库治理项目的基本骨架：

- `AGENTS.md`、`repo_protocol_standard.yaml`、`.cursor/rules/`：已有 Agent 执行边界与基础协议。
- `config/`：已有 `repos.yaml`、`repos.example.yaml`、`managed_files.yaml`、评分与优先级配置。
- `scripts/`：已有只读扫描、状态分析、Dashboard 生成、日报/周报、Prompt 生成、Feishu/OpenRouter opt-in 脚本与 `agent_gate.py`。
- `data/`：已有示例快照、状态、优先级、人类备注、本地导入示例。
- `dashboard/`：已有静态 Dashboard、Hub、generation review 页面。
- `docs/`：已有架构、安全、安装、调度、生命周期、OpenClaw、Cursor Automations、Feishu、Personal OS 远期路线等文档。
- `docs/rounds/`：已有历史 Round 00-24 文档。
- `reports/`：已有历史轮次报告、日报、周报、UI 检查、协议同步和优先级报告。
- `round_state/`：已有当前轮次与历史记录。
- `tests/`：已有 pytest 测试。

## 2. 基本形态判断

当前项目已经不是空白 Dashboard，而是具备“只读扫描 -> 状态分析 -> 优先级建议 -> 报告/Prompt/Dashboard”的 repo-ops-dashboard 基本形态。它能读取有限管理文件，生成状态和推进建议，并通过 Cursor/Codex/Automations/OpenClaw 规划进行下游协作。

## 3. Portfolio Governance 成熟度

当前仓库仍主要停留在“多仓库状态面板 + 编排脚本”阶段，尚未系统化升级为 portfolio governance。缺口包括：

- 缺少 `governance/` 作为机器权威治理资产入口。
- 缺少标准 `task_spec`、`proof_of_work`、`agent_run.jsonl`、`handoff_packet`。
- 缺少 `review_queue` 作为 Human-in-the-loop 决策中枢。
- 缺少文档级 `execpolicy` 与后续脚本化检查路线。
- 缺少 `eval_registry` 与统一 eval gate 设计。
- 缺少 `repo_context_index` 防止跨仓上下文爆炸的正式设计。

## 4. 治理资产现状

| 资产 | 当前状态 | 结论 |
| --- | --- | --- |
| project_registry | `config/repos.yaml` 已有登记雏形 | 需迁移/映射到 `governance/project_registry.example.yaml` |
| portfolio_state | 无正式模型 | 本轮新增示例 |
| task_spec | 无 | 本轮新增模板与示例 |
| proof_of_work | 无 | 本轮新增模板与示例 |
| review_queue | 无 | 本轮新增 |
| execpolicy | 无正式目录 | 本轮新增文档级规则 |
| agent_run | 无统一 JSONL 规范 | 本轮新增设计与 `.gitkeep` |
| eval_registry | 无 | 本轮新增 |
| repo_context_index | allowlist 中未正式纳入 | 本轮新增设计 |

## 5. 过期、重复、空洞文件

未发现需要硬删除的文件。需要标记关系的文件包括：

- 历史 `reports/round_02_completion_report.md` 与 `docs/rounds/round_02_readonly_scanner.md` 是旧 Round 02 资产，不应覆盖。
- `docs/personal_os_roadmap.md` 是早期 Personal OS 路线，后续由 `docs/roadmap_40_rounds.md` 承接为治理架构路线。
- `reports/openclaw_daily_brief.md` 与 `reports/daily_brief.md` 存在历史命名并存，后续可在清理轮合并引用。

## 6. Round 文档粗细

历史 `docs/rounds/round_00` 到 `round_24` 能表达目标和验收，但多数不是后续 Agent 可直接执行的完整任务规格。本轮建议新增架构路线总表，并从 Round 25 起使用更完整的任务规格模板。

## 7. 安全边界

当前安全边界已有基础：

- `.gitignore` 排除 `.env`、密钥、构建产物与本地数据。
- `scan_repos.py` 使用 allowlist 与 denylist，不做全量源码扫描。
- `AGENTS.md` 禁止读取密钥、修改被管理仓库、自动提交、自动删除。
- Playwright 仅用于本地 Dashboard 检查。

缺口：安全边界尚未以 `execpolicy`、`review_queue`、`eval_registry` 三者串联。

## 8. Playwright 准备

`requirements-dev.txt` 已包含 Playwright 与 pytest；`scripts/ui_check.py` 已存在，设计目标为本地 `file://` Dashboard 检查。Playwright 是否可运行取决于本机依赖和 Chromium 安装状态，需在验证阶段实际执行。

## 9. OpenClaw 接入状态

OpenClaw 当前是规划/Skill 层接入，已有文档和 legacy Skill。现有实现不应被理解为主力编程 Agent，也不应越界修改业务仓库。本轮需要把 OpenClaw 重新定位为 Personal Agent OS 的“调度入口/提醒入口”。

## 10. 本轮建议修改范围

本轮应聚焦于治理层资产，不大规模改业务逻辑：

- 新增 `governance/` 核心目录和示例。
- 升级协议、README、AGENTS 与文档索引。
- 新增数据模型、审计、handoff、review、execpolicy、repo_context_index、eval gate 设计。
- 扩写 40 轮架构路线，并保留历史 Round 00-24。
- 增强 `agent_gate.py` 的治理资产检查。
- 不修改被管理业务仓库，不读取密钥，不调用外部 API，不接真实 OpenClaw/Feishu。
