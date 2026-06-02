# 40 轮治理架构路线

本路线是 Personal Agent OS 的架构路线。仓库历史执行轮次已完成 Round 00-24，因此从架构 Round 02 起映射到执行 Round 25 起，避免覆盖历史资产。

## 编号映射

- 历史仓库 Round 00-24：保留，不重命名。
- 架构 Round 02：本次执行为仓库 Round 25。
- 架构 Round 03-40：后续执行为仓库 Round 26-63。

## Round 00 - Bootstrap

- 目标：创建基础骨架、协议、AGENTS、Dashboard 示例。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_00_bootstrap.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 01 - Independent Governance Audit & Playwright Preparation

- 目标：复核上一轮产物、加入 Playwright、扩写初步路线。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_01_independent_governance_audit_&_playwright_preparation.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 02 - Architecture Absorption & Personal Agent OS Upgrade

- 目标：吸收参考框架方法论，升级为治理层架构。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_25_architecture_absorption_personal_agent_os_upgrade.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：true。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 03 - Project Registry MVP

- 目标：实现 project_registry.yaml，登记核心项目。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_26_project_registry_mvp.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 04 - Portfolio State Snapshot

- 目标：实现 portfolio_state.yaml/json 快照。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_27_portfolio_state_snapshot.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 05 - Governance Task Queue

- 目标：实现 governance_task 队列和 task_spec 读取。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_28_governance_task_queue.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 06 - Proof of Work System

- 目标：实现 proof_of_work 模板、生成、校验。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_29_proof_of_work_system.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 07 - Agent Run JSONL Audit Trail

- 目标：实现 agent_run.jsonl 记录规范和手动记录工具。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_30_agent_run_jsonl_audit_trail.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 08 - Review Queue MVP

- 目标：实现 review_queue 读写与人工决策状态。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_31_review_queue_mvp.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：true。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 09 - Execpolicy Checker

- 目标：将 execpolicy 文档约束部分脚本化。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_32_execpolicy_checker.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 10 - Repo Context Index MVP

- 目标：为业务仓库生成轻量 repo_context_index。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_33_repo_context_index_mvp.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 11 - Readonly Repo Scanner V2

- 目标：严格 allowlist 扫描 README/AGENTS/协议/round_state。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_34_readonly_repo_scanner_v2.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 12 - Status Analyzer V2

- 目标：根据 registry、snapshot、round_state 分析项目健康度。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_35_status_analyzer_v2.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 13 - Priority Scoring System

- 目标：实现 impact × urgency × unblock - cost - risk 评分。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_36_priority_scoring_system.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 14 - Lifecycle Rules

- 目标：实现 idea/bootstrap/active/blocked/maintenance/frozen/archived/abandoned。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_37_lifecycle_rules.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 15 - Blocker Management

- 目标：定义 blocker 类型和超时升级。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_38_blocker_management.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 16 - Dashboard V2

- 目标：显示 portfolio_state、task_queue、review_queue、blockers。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_39_dashboard_v2.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 17 - Playwright Dashboard Validation

- 目标：用 Playwright 检查 Dashboard 渲染和截图。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_40_playwright_dashboard_validation.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 18 - Prompt Generator for Cursor

- 目标：根据 task_spec 生成 Cursor Prompt。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_41_prompt_generator_for_cursor.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 19 - Prompt Generator for Codex

- 目标：根据 task_spec 生成 Codex Prompt。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_42_prompt_generator_for_codex.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 20 - OpenClaw Orchestration Bridge

- 目标：让 OpenClaw 读取状态、触发报告、生成提醒，不改业务仓库。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_43_openclaw_orchestration_bridge.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：true。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 21 - Weekly Digest MVP

- 目标：生成 weekly_digest Markdown。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_44_weekly_digest_mvp.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 22 - Daily Briefing MVP

- 目标：生成每日建议。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_45_daily_briefing_mvp.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 23 - Eval Registry Script

- 目标：把 eval registry 中基础项脚本化。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_46_eval_registry_script.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 24 - Handoff Protocol Implementation

- 目标：生成 handoff_packet 并跟踪返回结果。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_47_handoff_protocol_implementation.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 25 - Failure Recovery & Retry Policy

- 目标：定义 retry_count、failure_class、checkpoint_id、review_queue 升级。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_48_failure_recovery_retry_policy.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 26 - Checkpoint Snapshot

- 目标：实现 portfolio_state 定期快照。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_49_checkpoint_snapshot.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 27 - Skill / Playbook Candidate Extraction

- 目标：从成功任务提取 playbook 候选，人工批准。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_50_skill_playbook_candidate_extraction.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：true。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 28 - Project Rule Promotion

- 目标：将成功规则推广到项目规则，进入 review_queue。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_51_project_rule_promotion.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：true。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 29 - Cross-Repo Protocol Sync Suggestion

- 目标：只生成同步建议，不自动改业务仓库。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_52_cross_repo_protocol_sync_suggestion.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 30 - Budget & Cost Tracking

- 目标：按项目记录预算、模型成本、API 使用估算。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_53_budget_cost_tracking.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：true。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 31 - WIP Limit & Scheduling

- 目标：限制 in_progress 任务数量，防止多项目失控。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_54_wip_limit_scheduling.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 32 - Feishu/Lark Notification Planning

- 目标：规划飞书日报/周报，不接真实 API。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_55_feishu_lark_notification_planning.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：true。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 33 - Feishu/Lark Notification MVP

- 目标：接入飞书机器人，只推送低敏摘要。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_56_feishu_lark_notification_mvp.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：true。
- 是否允许外部 API：true。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 34 - Mac Local Notification

- 目标：本地通知今日建议和 blocker。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_57_mac_local_notification.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 35 - OpenClaw Daily Briefing Skill

- 目标：完善 OpenClaw skill 读取 digest 和 repo_status。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_58_openclaw_daily_briefing_skill.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 36 - Browser Dashboard Interaction

- 目标：Playwright 检查过滤器、复制 Prompt、卡片状态。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_59_browser_dashboard_interaction.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 37 - Multi-Agent Handoff Trial

- 目标：低风险任务测试 OpenClaw -> Cursor Prompt -> proof_of_work。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_60_multi_agent_handoff_trial.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：true。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 38 - Portfolio Governance Hardening

- 目标：加固安全、测试、错误处理、文档一致性。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_61_portfolio_governance_hardening.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 39 - Release / Backup / Restore

- 目标：实现备份、恢复、迁移、安装文档。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_62_release_backup_restore.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：false。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。

## Round 40 - Personal Agent OS Long-Term Integration

- 目标：长期整合项目、日程、学习、工作、财务投入、AI 额度、周报复盘。
- 不做什么：不读取密钥；不全量扫描业务源码；不自动修改被管理仓库；不自动提交或发布。
- 前置条件：上一轮 completion report 存在；基础 gate 可运行；HumanOwner 未冻结本项目。
- 输入文件：`repo_protocol_standard.yaml`, `AGENTS.md`, `round_state/current_round.yaml`。
- 输出文件：`docs/rounds/round_63_personal_agent_os_long_term_integration.md`，以及必要的治理资产、报告或脚本。
- 阶段任务：梳理现状；补齐机器可读 YAML/JSON；更新人类文档；加入最小脚本或示例；运行验证；写 completion report。
- 验收标准：产物存在；协议与 AGENTS 边界一致；验证命令有记录；失败项进入 blocker 或 review_queue。
- 风险点：范围膨胀、历史轮次冲突、过早自动化、误读业务仓库、通知或 API 越界。
- 推荐执行 Agent：Cursor。
- 是否需要 HITL：true。
- 是否允许外部 API：false。
- 是否允许修改被管理仓库：false。
- 与 Personal Agent OS 架构的关系：将本项目从状态面板推进为可审计、可验收、可交接的个人项目治理层。
