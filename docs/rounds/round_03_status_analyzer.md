# Round 03 - Status Analyzer

## 目标

- 根据 README、协议、round_state、CHANGELOG 推断仓库状态
- 生成 `health_score`
- 识别 `blockers` 与 `next_actions`
- 推荐 Cursor/Codex/OpenClaw/Human

## 不做什么

- 不分析业务源码
- 不自动修改被管理仓库
- 不调用外部 API 获取 GitHub 状态

## 前置条件

- `data/repo_snapshots.json` 存在
- `config/scoring_rules.yaml` 已配置

## 输入文件

- `data/repo_snapshots.json`
- `config/scoring_rules.yaml`

## 输出文件

- `data/repo_status.json`

## 阶段任务

### 阶段 1 — 规则引擎

- 缺失治理文件扣分
- warning 数量影响 health_score

### 阶段 2 — 卡点识别

- AGENTS.md / protocol 缺失 → blocker
- path missing → blocker

### 阶段 3 — Agent 推荐

- 治理缺失 → Human
- 可批量推进 → Codex
- 本地开发/UI → Cursor

## 验收标准

- 每仓有 health_score、priority、blockers、next_actions
- freeze/archive 候选标记合理
- 输出 JSON 符合 `docs/repo_status_schema.md`

## 风险点

- 规则过简导致误判
- 需 Human 复核 freeze/archive 候选

## 推荐执行 Agent

- Cursor / Codex

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
完善 analyze_repos.py 规则引擎，输出 repo_status.json。
验证：python3 scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
```
