# Orchestration Repo Scan Prompt

目标：只读扫描仓库 `{{repo_name}}` 的状态产物并生成调度建议（供 Cursor Automations / 编排 Agent 使用）。

输入：

- `data/repo_status.json`
- `reports/daily_repo_report.md`
- `reports/weekly_repo_report.md`

当前状态：

- 优先级：{{priority}}
- 健康分：{{health_score}}
- 卡点：{{blockers}}
- 下一步：{{next_actions}}
- 扫描 warning：{{warnings}}

输出：

- 今日建议推进仓库列表
- 风险提醒
- 给 Cursor/Codex 的执行提示词草案

边界：

- 不修改被管理业务仓库
- 不读取密钥文件
- 不调用外部 API（除非 Human opt-in LLM / 飞书发送）
