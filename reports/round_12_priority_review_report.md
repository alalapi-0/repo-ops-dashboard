# Round 12 Priority Review System — Completion Report

- **状态**: completed
- **执行者**: cursor
- **外部 API**: false

## 产出

| 文件 | 说明 |
|------|------|
| `config/priority_factors.yaml` | 多因素权重与阈值 |
| `scripts/priority_review.py` | 生成 `priority_board.json` 与 `priority_review.md` |
| `tests/test_priority_review.py` | 评分与 Human 覆盖单测 |
| `docs/priority_rules.md` | 补充 Round 12 复盘说明 |
| `scripts/generate_dashboard.py` | 卡片展示「优先级来源」 |
| `scripts/refresh_status.sh` | 链路中插入 priority_review |

## 验收

- 因素文档与配置完整
- `priority_review.py` 可生成报告
- Human 通过 `repos.yaml` 的 `priority_hint` 覆盖最终优先级
- pytest 16+ passed；ui_check PASS

## 下一轮

`round_13_cross_repo_protocol_sync`
