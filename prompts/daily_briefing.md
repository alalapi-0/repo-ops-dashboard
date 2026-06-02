# Daily Briefing Template (Governance MVP)

生成时间：{{generated_at}}

## 当前轮次

- round：`{{current_round}}`
- status：`{{round_status}}`
- next：`{{next_round}}`

## 今日最该推进（1–3 仓）

{{top_repos}}

## 今日暂缓 / 不该碰

{{defer_repos}}

## 待 HumanOwner 决策

{{review_queue_open}}

## 风险提醒

{{risk_notes}}

## 给 Cursor/Codex 的执行草案

{{cursor_codex_drafts}}

## 建议触发命令（默认 dry-run / 只读）

```bash
python3 scripts/agent_gate.py
python3 scripts/refresh_status.sh --example
python3 scripts/openclaw_orchestration_bridge.py --dry-run
```

## 短提醒（≤200 字）

{{short_reminder}}

---

边界：不读 `.env`、不改被管理业务仓库、不自动 commit/push。
