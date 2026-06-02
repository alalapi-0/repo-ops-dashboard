# Review Queue 设计

`governance/review_queue.yaml` 是 Human-in-the-loop 中枢。它记录需要 HumanOwner 明确决策的事项。

## 字段

- `review_id`：唯一 ID。
- `type`：决策类型，如 priority_conflict、publish_approval、project_archive。
- `project_id`：关联项目，可为空。
- `task_id`：关联任务，可为空。
- `prompt`：给 HumanOwner 的问题。
- `options`：允许选项。
- `context_refs`：上下文文件引用。
- `status`：open、decided、expired、cancelled。
- `decision`：最终决策。
- `decided_at`：决策时间。
- `expires_at`：可选过期时间。

## 规则

review_queue 只能由 HumanOwner 关闭。Agent 可以创建 review item、补充 context_refs、标记 blocker，但不得自行批准、发布、归档、删除、增加预算或写入长期记忆。
