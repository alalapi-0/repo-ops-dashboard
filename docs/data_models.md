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
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/task_specs/*.yaml` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/task_specs/*.yaml`
- 后续实现轮次：Round 28

```yaml
governance_task:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
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
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/review_queue.yaml` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/review_queue.yaml`
- 后续实现轮次：Round 31

```yaml
review_queue:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
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
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/task_specs/task_spec.template.yaml` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/task_specs/task_spec.template.yaml`
- 后续实现轮次：Round 28

```yaml
task_spec:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## proof_of_work

- 用途：任务完成后的产物、文件、验证、审计和已知问题
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/proof_of_work/*.json` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/proof_of_work/*.json`
- 后续实现轮次：Round 29

```yaml
proof_of_work:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
```

## agent_run_event

- 用途：JSONL 审计流的单行事件
- 字段：`id/name`、`status/lifecycle`、`project_id`、`context_refs`、`created_at/updated_at`、模型特有字段。
- 字段说明：标识字段用于关联；状态字段用于调度；上下文字段只传引用；时间字段用于审计。
- 示例：见 `governance/runs/{run_id}.jsonl` 或下方片段。
- 是否机器权威：是
- 对应文件路径：`governance/runs/{run_id}.jsonl`
- 后续实现轮次：Round 30

```yaml
agent_run_event:
  id: example
  status: proposed
  project_id: repo_ops_dashboard
  updated_at: '2026-06-02T00:00:00Z'
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
- 后续实现轮次：Round 32

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
