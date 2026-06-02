# Repo Context Index 设计

每个被管理业务仓库未来应提供 `repo_context_index.yaml`，作为低 token、可审计的默认上下文入口。

## 字段

```yaml
project_id:
repo_name:
summary:
domain:
current_stage:
key_files:
  -
key_commands:
  -
roadmap_summary:
known_blockers:
  -
last_change_summary:
next_actions:
  -
updated_at:
```

## 用途

- 防止每次 Agent 全量读取仓库。
- 为 OpenClaw/Cursor/Codex 提供低 token 上下文。
- 作为每次治理任务的默认入口。
- 支持跨仓状态汇总、优先级排序和 handoff。

## 脚本化（Round 33）

- `scripts/validate_repo_context_index.py`：校验字段与密钥样文本边界。
- `scripts/read_repo_context_index.py`：读取并摘要。
- `scripts/build_repo_context_index_stub.py`：从 `project_registry.yaml` 生成 stub（默认 stdout；仅可写入本仓库根或 `governance/stubs/`）。
- `repo_context_index.yaml` 位于各仓库根目录；本仓库已提供实例与 `governance/repo_context_index.example.yaml`。

## 边界

`repo_context_index.yaml` 不应包含密钥、账号、token、完整业务源码或长篇生成内容。
