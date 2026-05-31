# Round 12 - Priority Review System

## 目标

- 建立优先级复盘系统
- 综合多因素给出 priority 建议
- 支持 Human 覆盖

## 不做什么

- 不自动改变用户优先级（默认建议）
- 不读取财务/收入真实 API

## 前置条件

- `docs/priority_rules.md` 存在
- repo_status 含基础 priority 字段

## 输入文件

- `config/scoring_rules.yaml`
- `data/priority_board.example.json`
- Human 输入的复盘笔记（可选 Markdown）

## 输出文件

- `data/priority_board.json`（本地，gitignore）
- `reports/priority_review.md`

## 阶段任务

### 阶段 1 — 因素建模

考虑因素：
- 当前收入/工作相关性
- AI 项目主线相关性
- 短期可展示成果
- 组件复用度
- 资金/时间成本
- 是否被其他项目替代

### 阶段 2 — 评分脚本

- `scripts/priority_review.py` 读取因素配置
- 输出建议 priority 与理由

### 阶段 3 — 复盘报告

- 每周 Human Review 模板
- Dashboard 展示 priority 来源

## 验收标准

- 因素文档完整
- 脚本可生成 priority_review 报告
- Human 可手动覆盖 priority

## 风险点

- 主观因素难量化
- 过度自动化导致错误优先级

## 推荐执行 Agent

- Human（复盘）/ Cursor（脚本）

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
实现 priority_review.py，从配置因素生成 reports/priority_review.md。
priority 仅为建议，Human 在 repos.yaml 中最终确认。
```
