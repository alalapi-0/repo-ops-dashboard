# Daily Brief Template

生成时间：{{generated_at}}

## 今日最该推进（1–3 仓）

{{top_repos}}

## 今日暂缓 / 不该碰

{{defer_repos}}

## 风险提醒

{{risk_notes}}

## 建议触发命令（默认 dry-run / 只读）

```bash
python3 scripts/agent_gate.py
python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/generate_report.py --input data/repo_status.example.json
```

## 给 Cursor/Codex 的执行草案

{{cursor_codex_drafts}}

## 短提醒

{{short_reminder}}

---

边界：不读 `.env`、不改被管理业务仓库、不自动 commit。
