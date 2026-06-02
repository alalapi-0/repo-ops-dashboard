# OpenClaw Daily Briefing Skill

生成时间：{{generated_at}}

## 当前轮次

- round：`{{current_round}}`
- status：`{{round_status}}`
- next：`{{next_round}}`

## Repo Status 摘要

- 仓库数：{{repo_count}}
- 有卡点：{{blocked_repo_count}}
- 扫描时间：{{status_generated_at}}

## 今日最该推进（1–3 仓）

{{top_repos}}

## 今日暂缓 / 不该碰

{{defer_repos}}

## Daily Briefing 摘要

{{daily_briefing_excerpt}}

## Weekly Digest 摘要

{{weekly_digest_excerpt}}

## 待 HumanOwner 决策

{{review_queue_open}}

## 建议触发命令（默认 dry-run / 只读）

```bash
{{dry_run_commands}}
```

## 短提醒（≤200 字）

{{short_reminder}}

---

边界：不读 `.env`、不改被管理业务仓库、不自动 commit/push、不调用外部 API。
