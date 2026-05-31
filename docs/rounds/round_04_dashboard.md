# Round 04 - Dashboard UI

## 目标

- 生成可读静态 Dashboard
- 支持过滤（优先级、生命周期、Agent）
- 支持 freeze/archive 标记展示
- 支持一键复制 Prompt（客户端 JS）
- 引入 Playwright UI 检查

## 不做什么

- 不引入 React/Vue 等重型框架
- 不接后端 API
- 不登录任何网站

## 前置条件

- `data/repo_status.json` 或 example 可用
- `scripts/generate_dashboard.py` 基础版存在

## 输入文件

- `data/repo_status.json`
- `dashboard/style.css`, `dashboard/app.js`

## 输出文件

- `dashboard/index.html`（生成）
- `reports/ui_screenshots/*.png`（Playwright）

## 阶段任务

### 阶段 1 — 统计与卡片增强

- 总仓数、高优先级、blocked、freeze/archive 候选
- 卡片展示 lifecycle_status、last_checked

### 阶段 2 — 客户端过滤

- `app.js` 实现优先级/状态过滤
- 无框架纯 DOM 操作

### 阶段 3 — Prompt 复制与 UI 检查

- 每卡「复制 Prompt」按钮
- `ui_check.py` 验证渲染

## 验收标准

- Dashboard 在浏览器可打开
- 过滤功能可用
- Playwright 检查通过或 warning 可解释
- 统计数字与 JSON 一致

## 风险点

- 静态 HTML 过滤逻辑与生成脚本需同步
- Playwright 环境差异

## 推荐执行 Agent

- Cursor

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
增强 Dashboard：过滤、Prompt 复制、lifecycle 字段。
生成：python3 scripts/generate_dashboard.py --input data/repo_status.example.json
检查：python3 scripts/ui_check.py --file dashboard/index.html --headless true
```
