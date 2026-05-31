# Round 09 - Playwright UI Check

## 目标

- 使用 Playwright 打开本地 Dashboard
- 自动截图到 `reports/ui_screenshots/`
- 检查主要卡片渲染、标题、容器
- 检查过滤器与 Prompt 复制按钮（Round 04 完成后）
- **不登录**任何网站

## 不做什么

- 不访问外网 URL
- 不使用真实浏览器账号
- 不上传截图

## 前置条件

- `dashboard/index.html` 已生成
- `requirements-dev.txt` 与 Playwright chromium 已安装

## 输入文件

- `dashboard/index.html`
- `scripts/ui_check.py`

## 输出文件

- `reports/ui_check_report.md`
- `reports/ui_screenshots/dashboard.png`

## 阶段任务

### 阶段 1 — 基础检查（Round 1 已完成）

- 标题、容器、repo-card 计数
- file:// 本地打开

### 阶段 2 — 元素断言扩展

- 统计区数字与 JSON 一致（可选 DOM 解析）
- freeze/archive badge 存在性

### 阶段 3 — 集成 agent_gate

- agent_gate 检查 ui_check 仅本地访问
- CI 可选运行（无 browser 时 skip）

## 验收标准

- `ui_check.py` 本地 PASS 或合理 WARNING
- 未安装 Playwright 时 exit 2 且提示清晰
- 不影响核心扫描脚本

## 风险点

- CI 无 chromium 时失败
- headless 渲染差异

## 推荐执行 Agent

- Cursor / Codex

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
运行：python3 scripts/ui_check.py --file dashboard/index.html --screenshot reports/ui_screenshots/dashboard.png --headless true
扩展断言：过滤器、复制按钮（Round 04 后）。
```
