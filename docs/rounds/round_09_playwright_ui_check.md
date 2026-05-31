# Round 09 - Playwright UI Check

## 目标

- 用 Playwright 检查 Dashboard 页面
- 自动截图
- 检查卡片渲染
- 检查过滤器
- 不接真实浏览器账号

## 不做什么

- 不做端到端业务流程账号登录

## 输入文件

- `dashboard/index.html`
- `data/repo_status.json`

## 输出文件

- `artifacts/` 下的截图与检查报告

## 具体阶段

1. 本地页面加载检测
2. 元素断言
3. 截图与报告

## 验收标准

- 关键 UI 元素通过自动检查

## 风险

- 本地环境差异导致测试不稳定

## 推荐执行 Agent

- Codex
