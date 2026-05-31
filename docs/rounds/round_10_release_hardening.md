# Round 10 - Release Hardening

## 目标

- 强化测试与 `agent_gate`
- 整理安装文档与长期使用指南
- 支持稳定日常运行

## 不做什么

- 不大规模重构
- 不引入微服务或数据库
- 不自动部署到云

## 前置条件

- Round 00–09 核心功能可用
- 验证命令链稳定

## 输入文件

- 全部 scripts、docs、config

## 输出文件

- `docs/installation.md`
- 增强的 `agent_gate.py` 检查项
- 可选 `tests/` 目录

## 阶段任务

### 阶段 1 — 测试

- pytest 覆盖 analyze、gate 核心逻辑
- 示例数据 fixture

### 阶段 2 — 文档

- 安装、调度、故障排查
- Agent 使用手册索引

### 阶段 3 — Gate 硬化

- 全 round 文档章节检查
- secret/env 跟踪检查

## 验收标准

- `python3 scripts/agent_gate.py` PASS 或仅可解释 WARNING
- 安装文档可让新 Agent 30 分钟内跑通
- CHANGELOG 完整

## 风险点

- 过度测试维护成本
- 文档与代码漂移

## 推荐执行 Agent

- Codex / Cursor

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
添加 pytest、installation.md，硬化 agent_gate。
目标：日常一条命令刷新 status + dashboard + report + ui_check。
```
