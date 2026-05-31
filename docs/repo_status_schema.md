# repo_status Schema 说明

`data/repo_status.json` 推荐字段：

- `generated_at`: 生成时间
- `repos`: 仓库数组
  - `name`
  - `path`
  - `type`
  - `status`
  - `current_stage`
  - `health_score`
  - `priority`
  - `blockers`
  - `next_actions`
  - `recommended_agent`
  - `freeze_candidate`
  - `archive_candidate`
  - `lifecycle_status`
  - `last_checked`
  - `warnings`（非阻断性扫描告警，可选）

该结构用于 Dashboard 展示与日报/周报生成。
