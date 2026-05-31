# OpenClaw Daily Brief Template

生成时间：2026-05-31 20:18 UTC

## 今日最该推进（1–3 仓）

1. **repo-ops-dashboard**（Cursor）— 处理扫描 warning 并补齐可选治理文件；卡点：无卡点
2. **novel-continuation-agent**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：repo_protocol_standard.yaml missing
3. **light_novel**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：AGENTS.md missing; repo_protocol_standard.yaml missing

## 今日暂缓 / 不该碰

- **ai-manga**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：README.md missing; AGENTS.md missing; repo_protocol_standard.yaml missing
- **old_demo_placeholder**（Human）— 确认仓库路径是否有效，或从登记中归档；卡点：repository path missing

## 风险提醒

- 有卡点仓库 4 个：light_novel, ai-manga, novel-continuation-agent, old_demo_placeholder
- 归档候选：old_demo_placeholder

## 建议触发命令（默认 dry-run / 只读）

```bash
python3 scripts/agent_gate.py
python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/generate_report.py --input data/repo_status.example.json
```

## 给 Cursor/Codex 的执行草案

- **repo-ops-dashboard** → Cursor：无
- **novel-continuation-agent** → Human：repo_protocol_standard.yaml missing
- **light_novel** → Human：AGENTS.md missing; repo_protocol_standard.yaml missing

## 短提醒

今日优先推进：repo-ops-dashboard, novel-continuation-agent。暂缓 2 仓勿动。OpenClaw 只读编排，编程交给 Cursor/Codex。

---

边界：不读 `.env`、不改被管理业务仓库、不自动 commit。
