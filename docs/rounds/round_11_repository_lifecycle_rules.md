# Round 11 - Repository Lifecycle Rules

## 目标

- 建立仓库生命周期规则与状态机
- 定义进入 frozen/archived/abandoned 的条件
- 定义重新激活与「建议删除但不自动删除」规则

## 不做什么

- 不自动删除仓库
- 不自动 git archive
- 不修改被管理仓库状态文件（仅建议）

## 前置条件

- `analyze_repos.py` 可输出 status
- Human 可复核生命周期变更

## 输入文件

- `config/scoring_rules.yaml`
- `data/repo_status.json`

## 输出文件

- `docs/lifecycle_rules.md`
- 更新的 scoring_rules（lifecycle 字段）

## 阶段任务

### 阶段 1 — 状态定义

状态包括：`idea`, `bootstrap`, `active`, `blocked`, `maintenance`, `frozen`, `archived`, `abandoned`

### 阶段 2 — 转换规则

- **frozen**：长期无 commit、Human 标记、或 health_score 持续低于阈值
- **archived**：项目完成或替代、path missing 超过 N 天
- **重新激活**：Human 决定 + 新 round 计划
- **建议删除**：abandoned + path missing + 无备份需求 → 报告建议，Human 手动删除

### 阶段 3 — 分析器集成

- `lifecycle_status` 写入 repo_status
- Dashboard 展示生命周期标签

## 验收标准

- 文档定义 8 状态及转换条件
- analyze 输出 lifecycle_status
- 无自动删除逻辑

## 风险点

- 误判 active 为 abandoned
- Human 未复核自动 freeze 建议

## 推荐执行 Agent

- Cursor / Human（最终状态）

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
编写 docs/lifecycle_rules.md，更新 scoring_rules 与 analyze_repos 输出 lifecycle_status。
禁止自动删除，仅报告建议。
```
