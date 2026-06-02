# Handoff 协议

Handoff 是治理层把任务交给 Cursor、Codex、OpenClaw 或业务项目 Agent 的结构化包。它传递上下文引用，不传全量上下文。

## 流向

- governance agent -> Cursor：本仓库脚本、Dashboard、协议与文档实现。
- governance agent -> Codex：边界清楚的批量任务、测试修复、PR/提交建议。
- governance agent -> OpenClaw：读取状态、生成提醒、触发只读脚本、生成 Prompt。
- OpenClaw -> repo-ops-dashboard：读取 digest、portfolio_state、review_queue，返回今日建议。
- repo-ops-dashboard -> business repo：只传 task_spec、context_refs、allowed_files，不直接写业务仓库。
- business repo -> proof_of_work：业务 Agent 完成后提交证明、验证结果和产物路径。

## handoff_packet 字段

```yaml
handoff_id:
parent_task_id:
target_agent:
working_directory:
task_spec_path:
context_refs:
  -
allowed_files:
  -
denied_files:
  -
confirmation_policy:
execpolicy_profile:
expected_artifacts:
  -
timeout:
return_contract:
```

## 强制规则

- 传 `context_refs`，不传全量上下文。
- 传文件指针，不传所有源码。
- 每次 handoff 必须绑定 `working_directory`。
- 高风险动作必须声明 `confirmation_policy` 并进入 `review_queue`。
