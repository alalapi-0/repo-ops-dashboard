# Round 03 - Status Analyzer

## 目标

- 完成状态分析器
- 规则式判断项目状态
- 计算 `health_score`
- 输出 `blockers` / `next_actions` / `recommended_agent`

## 不做什么

- 不调用外部 API
- 不做 LLM 推理分析

## 输入文件

- `data/repo_snapshots.json`
- `config/scoring_rules.yaml`

## 输出文件

- `data/repo_status.json`

## 具体阶段

1. 规则加载
2. 维度评分
3. 优先级判断
4. 建议生成

## 验收标准

- 输出字段完整可用于 Dashboard

## 风险

- 规则阈值需后续迭代

## 推荐执行 Agent

- Codex
