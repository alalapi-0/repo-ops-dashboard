# Round 15 - Long-Term Personal Operating System

## 目标

- 远期规划：将 repo-ops-dashboard 升级为个人项目操作系统的核心模块
- **本轮只做规划，不实现**

## 不做什么

- 不实现日程/财务/AI 额度追踪
- 不接第三方日历/记账 API
- 不扩大全量扫描范围

## 前置条件

- Round 00–14 核心仓库管理能力稳定
- Human 明确个人 OS 优先级

## 输入文件

- 现有 architecture、round 路线图
- Human 笔记（可选）

## 输出文件

- `docs/personal_os_roadmap.md`（规划文档）

## 阶段任务

### 阶段 1 — 模块愿景

规划整合：
- 项目（repos）
- 日程
- 学习
- 工作
- 财务投入
- AI 额度消耗
- 周报复盘

### 阶段 2 — 边界与接口

- 哪些模块只读聚合
- 哪些需独立工具
- repo-ops-dashboard 保持「仓库中枢」角色

### 阶段 3 — 分期路线图

- Phase A/B/C 里程碑
- 每阶段推荐 Agent 与验收标准

## 验收标准

- `docs/personal_os_roadmap.md` 存在且结构完整
- 明确不替代 Cursor/Codex 编程角色
- 无实现代码变更要求

## 风险点

- 范围膨胀失去焦点
- 与 repo-ops 核心使命混淆

## 推荐执行 Agent

- Human（愿景）/ Cursor（文档）

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
撰写 docs/personal_os_roadmap.md，描述个人 OS 远期模块与 repo-ops-dashboard 的关系。
仅文档，不写实现代码。OpenClaw 未来做跨模块提醒入口。
```
