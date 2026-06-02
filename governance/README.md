# Governance

`governance/` 是 repo-ops-dashboard 的机器可读治理资产入口。它承载 Personal Agent OS / Portfolio Orchestrator 的核心状态、任务、审计、验收、权限与人工决策队列。

## 原则

- YAML/JSON 是机器权威，Markdown 是人类视图。
- 每个治理任务必须有 `task_spec`、工作目录、验收标准和 `proof_of_work`。
- 每次 Agent 执行必须能落到 `governance/runs/{run_id}.jsonl` 的审计事件模型。
- 任何高风险决策必须进入 `review_queue.yaml`，只能由 HumanOwner 关闭。
- 被管理业务仓库默认只读；本项目可写；密钥、`.env`、token、私钥不可读。

## 目录

- `project_registry.yaml`：机器可读项目登记（由 `scripts/sync_project_registry.py` 从 `config/repos.yaml` 同步）。
- `project_registry.example.yaml`：项目登记示例与字段参考。
- `portfolio_state.yaml`：组合状态快照（`scripts/sync_portfolio_state.py` 从 registry + repo status 生成）。
- `portfolio_state.example.yaml`：组合状态快照示例。
- `governance_task_queue.yaml`：治理任务队列（`scripts/sync_governance_task_queue.py` 从 `task_specs/` 同步）。
- `governance_task_queue.example.yaml`：任务队列示例。
- `task_specs/`：治理任务模板和示例（`scripts/read_task_spec.py` 读取/校验单个规格）。
- `proof_of_work/`：任务完成证明模板和示例（`scripts/read_proof_of_work.py` 读取/校验）。
- `proof_of_work_registry.yaml`：完成证明注册表（`scripts/sync_proof_of_work_registry.py` 同步）。
- `proof_of_work_registry.example.yaml`：注册表示例。
- `runs/`：未来审计 JSONL 输出目录。
- `review_queue.yaml`：人工决策队列。
- `execpolicy/`：文档级执行边界。
- `evals/registry.yaml`：验收 gate 注册表。
- `playbooks/`：可复用流程候选。
- `skills/`：可沉淀为 Agent Skill 的候选说明。
- `digests/`：日报/周报治理摘要输出位置。
