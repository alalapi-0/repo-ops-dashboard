# Priority Scoring Design (Round 36)

## 公式

```
priority_score = impact × urgency × unblock / product_scale - cost - risk
```

默认 `product_scale=10`（乘积最大约 1000，换算为 0–100 量级分数），各乘数因子取值 0–10，`cost`/`risk` 为扣分项（0–50）。

## 因子含义

| 因子 | 含义 |
|------|------|
| impact | 类型主线权重 + 健康度加成 + registry 匹配 |
| urgency | 阻断、冻结候选、路径缺失 |
| unblock | 无阻断、有 next_round / next_actions、无 warnings |
| cost | warnings 数量、freeze 维护成本 |
| risk | 归档候选、低健康分 |

## 配置

- Live：`config/priority_scoring_policy.yaml`
- 示例：`governance/priority_scoring_policy.example.yaml`
- 校验：`scripts/validate_priority_scoring_policy.py`
- 计算：`scripts/priority_scoring.py`（由 `analyze_repos.py` 写入 `repo_status`）

## 输出字段

`repo_status` 每仓增加：

- `priority_score`
- `priority_score_band`（high / medium / low）
- `priority_score_breakdown`

`sync_portfolio_state.py` 将 `priority_score` 同步到 `governance/portfolio_state.yaml`。

## 与 Round 12 的关系

`scripts/priority_review.py` 仍使用 `config/priority_factors.yaml` 生成复盘报告；Round 36 分数供分析器与 portfolio 排序，不替代 Human `priority_hint` 覆盖。
