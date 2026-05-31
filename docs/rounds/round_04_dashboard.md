# Round 04 - Dashboard

## 目标

- 生成更好看的静态 Dashboard
- 支持过滤：高优先级、卡住、冻结候选、归档候选
- 支持一键复制 Prompt

## 不做什么

- 不引入前端框架
- 不依赖后端服务

## 输入文件

- `data/repo_status.json`

## 输出文件

- `dashboard/index.html`
- `dashboard/style.css`
- `dashboard/app.js`

## 具体阶段

1. 卡片视图优化
2. 过滤器实现
3. 交互增强

## 验收标准

- 本地双击可打开
- 过滤功能可用

## 风险

- 纯静态页面复杂度上升

## 推荐执行 Agent

- Cursor
