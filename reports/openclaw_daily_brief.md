# OpenClaw Daily Brief Template

生成时间：2026-05-31 19:30 UTC

## 今日最该推进（1–3 仓）

1. **repo-ops-dashboard**（Cursor）— 处理扫描 warning 并补齐可选治理文件；卡点：无卡点
2. **ai-anime-short-factory**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：repo_protocol_standard.yaml missing
3. **novel-continuation-agent**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：repo_protocol_standard.yaml missing

## 今日暂缓 / 不该碰

- **ai-manga**（Human）— 目录为空：归档登记或恢复项目内容；卡点：repository directory empty
- **computer_study_plan**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：repo_protocol_standard.yaml missing
- **pixel-world-asset-forge**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：AGENTS.md missing; repo_protocol_standard.yaml missing
- **agent-experiments**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：README.md missing; AGENTS.md missing; repo_protocol_standard.yaml missing
- **ai-anime-short-factory-external**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：README.md missing; AGENTS.md missing; repo_protocol_standard.yaml missing
- **api-mini-labs**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：AGENTS.md missing; repo_protocol_standard.yaml missing
- **audiobook-cleaner-lab**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：repo_protocol_standard.yaml missing
- **resilient-personal-network**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：AGENTS.md missing; repo_protocol_standard.yaml missing
- **tool-mini-labs**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：AGENTS.md missing; repo_protocol_standard.yaml missing
- **typing-practice-app**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：AGENTS.md missing; repo_protocol_standard.yaml missing
- **youtube_hq_downloader**（Human）— 补齐缺失治理文件（AGENTS.md / protocol / README）；卡点：AGENTS.md missing; repo_protocol_standard.yaml missing

## 风险提醒

- 有卡点仓库 16 个：novel-continuation-agent, ai-manga, ai-anime-short-factory, wechat-article-scheduler, light_novel
- 归档候选：ai-manga

## 建议触发命令（默认 dry-run / 只读）

```bash
python3 scripts/agent_gate.py
python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python3 scripts/generate_report.py --input data/repo_status.example.json
```

## 给 Cursor/Codex 的执行草案

- **repo-ops-dashboard** → Cursor：无
- **ai-anime-short-factory** → Human：repo_protocol_standard.yaml missing
- **novel-continuation-agent** → Human：repo_protocol_standard.yaml missing

## 短提醒

今日优先推进：repo-ops-dashboard, ai-anime-short-factory。暂缓 11 仓勿动。OpenClaw 只读编排，编程交给 Cursor/Codex。

---

边界：不读 `.env`、不改被管理业务仓库、不自动 commit。
