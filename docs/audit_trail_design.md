# 审计轨迹设计

## 文件位置

`governance/runs/{run_id}.jsonl` 是未来每次 Agent 执行的审计轨迹。每行是一个独立 JSON 事件，便于追加、流式读取和故障恢复。

## 事件字段

- `event_type`：事件类型。
- `timestamp`：ISO 8601 时间。
- `task_id`：关联治理任务。
- `project_id`：关联项目。
- `agent_type`：Cursor、Codex、OpenClaw、Automation 等。
- `cwd`：执行工作目录。
- `payload`：结构化事件载荷。
- `error`：错误信息，可为空。
- `proof_of_work_path`：完成证明路径，可为空。

## 事件类型

- `task_created`
- `task_assigned`
- `handoff_created`
- `run_started`
- `command_planned`
- `command_executed`
- `file_read`
- `file_written`
- `validation_started`
- `validation_finished`
- `blocker_detected`
- `review_requested`
- `proof_submitted`
- `task_completed`
- `task_failed`

## 示例

```json
{"event_type":"run_started","timestamp":"2026-06-02T00:00:00Z","task_id":"task_repo_ops_round_25","project_id":"repo_ops_dashboard","agent_type":"Cursor","cwd":"/Users/alalapi/PycharmProjects/repo-ops-dashboard","payload":{"round":"25"},"error":null,"proof_of_work_path":null}
```
