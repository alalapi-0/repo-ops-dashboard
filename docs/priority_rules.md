# 优先级规则

## 高优先级

- active project
- has clear next action
- related to current AI/product roadmap

## 中优先级

- useful but not urgent
- needs governance cleanup

## 低优先级

- old demo
- unclear value

## 冻结候选

- no clear next action
- no recent update
- duplicated with another repo

## 归档候选

- repository path missing / directory empty（自动）
- obsolete demo
- no README and no future plan

## 治理评分（Round 36）

`analyze_repos.py` 按 `config/priority_scoring_policy.yaml` 计算 `priority_score`（impact × urgency × unblock − cost − risk），写入 `repo_status` 与 `portfolio_state`。

## 多因素复盘（Round 12）

算法脚本 `scripts/priority_review.py` 读取 `config/priority_factors.yaml`，结合 `repo_status` 与 `repos.yaml` 中的 `priority_hint` 生成 `reports/priority_review.md`。

- **Human 覆盖**：在 `config/repos.yaml` 设置 `priority_hint: high|medium|low` 后，Dashboard 显示「人工覆盖」。
- **仅建议**：未设置 hint 时，按 type、health、blocker/freeze/archive 扣分后给出 suggested priority。
