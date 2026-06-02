# 数据模型

本页定义 Personal Agent OS / Portfolio Orchestrator 的核心数据模型。YAML/JSON 是机器权威，Markdown 是人类视图。

## project_registry

- 用途：登记所有被治理项目、生命周期、路径、默认 Agent 与上下文入口
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/project_registry.example.yaml` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/project_registry.yaml`（权威）；`governance/project_registry.example.yaml`（示例）
- 同步命令：`python3 scripts/sync_project_registry.py`（`--dry-run` 仅校验）
- 实现轮次：Round 26（已完成 MVP）

```yaml
project_registry:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## portfolio_state

- 用途：记录组合层状态快照、健康度、WIP、blocker 与优先级
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/portfolio_state.example.yaml` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/portfolio_state.yaml`（权威）；`governance/portfolio_state.example.yaml`（示例）
- 同步命令：`python3 scripts/sync_portfolio_state.py`（`--dry-run` 仅校验；默认读 `data/repo_status.example.json`）
- 实现轮次：Round 27（已完成 MVP）

```yaml
portfolio_state:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## governance_task

- 用途：描述治理任务队列中的单个工作单元
- 字段：`task_id`、`project_id`、`status`、`priority`、`assigned_agent`、`task_spec_path`、`is_active` 等。
- 字段说明：队列条目由 `task_specs` 同步生成；完整规格见对应 `task_spec` 文件。
- 示例：见 `governance/governance_task_queue.example.yaml` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/governance_task_queue.yaml`（权威）；`governance/task_specs/*.yaml`（规格源）
- 同步命令：`python3 scripts/sync_governance_task_queue.py`（`--dry-run` / `--json` 仅输出）
- 读取命令：`python3 scripts/read_task_spec.py <path>`
- 实现轮次：Round 28（已完成 MVP）

```yaml
governance_task:
  task_id: task_example_001
  status: proposed
  project_id: repo_ops_dashboard
  task_spec_path: governance/task_specs/example_task_spec.yaml
```

## agent_assignment

- 用途：记录任务分配给 Cursor/Codex/OpenClaw/Human 的原因和权限
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/task_specs/*.yaml` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/task_specs/*.yaml`
- 后续实现轮次：Round 28

```yaml
agent_assignment:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## review_queue

- 用途：记录必须由 HumanOwner 决策的 HITL 项
- 字段：`review_id`、`type`、`project_id`、`task_id`、`prompt`、`options`、`context_refs`、`status`、`decision`、`decided_at`、`expires_at`。
- 字段说明：`status=open` 时 `decision`/`decided_at` 必须为 null；仅 HumanOwner 可通过 `close_review_queue_item.py` 关闭。
- 示例：见 `governance/review_queue.yaml` 或 `review_queue.example.yaml`。
- 是否机器权威：是
- 对应文件路径：`governance/review_queue.yaml`
- 读取命令：`python3 scripts/read_review_queue.py --status open`
- 实现轮次：Round 31（已完成 MVP）

```yaml
review_id: rq_example_001
type: governance_policy
status: open
decision: null
```

## weekly_digest

- 用途：面向人类的每周组合摘要
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/digests/weekly/*.md` 或下方片段。
- 是否机器权威：否，源自状态
- 对应文件路径：`governance/digests/weekly/*.md`
- 后续实现轮次：Round 44

```yaml
weekly_digest:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## status_snapshot

- 用途：扫描和分析后的状态快照
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `data/repo_snapshots*.json / data/repo_status*.json` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`data/repo_snapshots*.json / data/repo_status*.json`
- 后续实现轮次：Round 27

```yaml
status_snapshot:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## task_spec

- 用途：每个任务的目标、范围、目录、验收、权限与验证命令
- 字段：`task_id`、`project_id`、`working_directory`、`assigned_agent`、`acceptance_criteria`、`validation_commands`、`execpolicy_profile` 等。
- 字段说明：模板见 `task_spec.template.yaml`；非模板 YAML 由 `sync_governance_task_queue.py` 汇入队列。
- 示例：见 `governance/task_specs/example_task_spec.yaml` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/task_specs/*.yaml`（不含 `task_spec.template.yaml`）
- 读取命令：`python3 scripts/read_task_spec.py governance/task_specs/example_task_spec.yaml`
- 实现轮次：Round 28（已完成 MVP）

```yaml
task_spec:
  task_id: task_example_001
  status: proposed
  project_id: repo_ops_dashboard
  working_directory: /path/to/project
```

## proof_of_work

- 用途：任务完成后的产物、文件、验证、审计和已知问题
- 字段：`task_id`、`project_id`、`status`、`artifacts`、`validation_commands`、`tests_passed`、`audit_run_path` 等。
- 字段说明：模板见 `proof_of_work.template.json`；非模板 JSON 由 `sync_proof_of_work_registry.py` 汇入注册表。
- 示例：见 `governance/proof_of_work/example_proof_of_work.json` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/proof_of_work/*.json`（不含模板）；`governance/proof_of_work_registry.yaml`（索引）
- 同步命令：`python3 scripts/sync_proof_of_work_registry.py`（`--dry-run` / `--json`）
- 读取命令：`python3 scripts/read_proof_of_work.py governance/proof_of_work/example_proof_of_work.json`
- 实现轮次：Round 29（已完成 MVP）

```yaml
proof_of_work:
  task_id: task_example_001
  project_id: repo_ops_dashboard
  status: completed
  tests_passed: false
```

## agent_run_event

- 用途：JSONL 审计流的单行事件
- 字段：`event_type`、`timestamp`、`task_id`、`project_id`、`agent_type`、`cwd`、`payload`、`error`、`proof_of_work_path`。
- 字段说明：每行一个 JSON 对象；`event_type` 见 `docs/audit_trail_design.md`；`payload` 为结构化载荷。
- 示例：见 `governance/runs/example_run.jsonl` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/runs/{run_id}.jsonl`
- 读取命令：`python3 scripts/read_agent_run.py governance/runs/example_run.jsonl`
- 记录命令：`python3 scripts/record_agent_run_event.py --run-id <id> --event-type run_started --task-id task_x --dry-run`
- 实现轮次：Round 30（已完成 MVP）

```json
{"event_type":"run_started","timestamp":"2026-06-02T00:00:00Z","task_id":"task_example_001","project_id":"repo_ops_dashboard","agent_type":"Cursor","cwd":"/path/to/repo","payload":{},"error":null,"proof_of_work_path":null}
```

## handoff_packet

- 用途：治理层交给执行 Agent 的结构化任务包
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `未来 governance/handoffs/*.yaml` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`未来 governance/handoffs/*.yaml`
- 后续实现轮次：Round 47

```yaml
handoff_packet:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## repo_context_index

- 用途：每个业务仓库的低 token 上下文入口
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `业务仓库 repo_context_index.yaml` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`业务仓库 repo_context_index.yaml`
- 后续实现轮次：Round 33

```yaml
repo_context_index:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## eval_registry

- 用途：验收 gate 注册表
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/evals/registry.yaml` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/evals/registry.yaml`
- 后续实现轮次：Round 46

```yaml
eval_registry:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## execpolicy_profile

- 用途：执行权限和确认边界
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/execpolicy/profiles/*.rules` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/execpolicy/profiles/*.rules`
- 后续实现轮次：Round 32（已实现 `scripts/validate_execpolicy.py`）

```yaml
execpolicy_profile:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## playbook

- 用途：成功流程沉淀候选
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/playbooks/**/README.md` 或下方片段。
- 是否机器权威：否，需人工批准
- 对应文件路径：`governance/playbooks/**/README.md`
- 后续实现轮次：Round 50

```yaml
playbook:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## skill

- 用途：可被 Agent 调用的能力说明
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/skills/README.md / .cursor skills` 或下方片段。
- 是否机器权威：否，需人工批准
- 对应文件路径：`governance/skills/README.md / .cursor skills`
- 后续实现轮次：Round 50

```yaml
skill:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## project_rule

- 用途：项目级长期规则
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `AGENTS.md / .cursor/rules/*.mdc` 或下方片段。
- 是否机器权威：是，但写入需 HITL
- 对应文件路径：`AGENTS.md / .cursor/rules/*.mdc`
- 后续实现轮次：Round 51

```yaml
project_rule:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```
