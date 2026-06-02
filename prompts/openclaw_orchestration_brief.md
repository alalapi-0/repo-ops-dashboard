# OpenClaw Orchestration Brief

生成时间：{{generated_at}}

## 当前轮次

- round：`{{current_round}}`
- status：`{{round_status}}`
- next：`{{next_round}}`

## Portfolio 摘要

{{portfolio_summary}}

## 待 HumanOwner 决策（review_queue）

{{review_queue_open}}

## 活跃治理任务

{{active_tasks}}

## 今日最该推进（1–3 项目）

{{top_projects}}

## 今日暂缓 / 不该碰

{{defer_projects}}

## 建议触发命令（默认 dry-run / 只读）

```bash
{{dry_run_commands}}
```

## 短提醒（≤200 字）

{{short_reminder}}

---

边界：不读 `.env`、不改被管理业务仓库、不自动 commit/push、不调用外部 API。
