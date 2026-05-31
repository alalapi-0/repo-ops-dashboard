# AGENTS.md

## 1) 项目身份

本项目为 `repo-ops-dashboard`，用于管理多个本地项目仓库的状态、优先级、卡点与下一步行动建议。

## 2) Agent 分工

- CursorAgent：本地开发、脚本实现、Dashboard UI、文档维护。
- CodexAgent：清晰边界内的批量推进、测试、自动修复、PR。
- OpenClawAgent：后续用于调度、提醒、读取状态、触发报告，不作为主要编程 Agent。
- HumanOwner：最终决定优先级、冻结、归档与推进方向。

## 3) 绝对禁止

- 禁止读取任何 `.env`
- 禁止打印任何 API Key
- 禁止修改被管理的业务仓库
- 禁止全量递归扫描所有仓库
- 禁止自动删除仓库
- 禁止自动 git commit
- 禁止自动接入通知平台
- 禁止在 Round 0 调用外部 API

## 4) Round 执行协议

每一轮必须：

1. 读取 `repo_protocol_standard.yaml`
2. 读取 `round_state/current_round.yaml`
3. 读取对应 `docs/rounds/round_xx_*.md`
4. 输出计划
5. 执行有限范围修改
6. 运行验证命令
7. 更新 `CHANGELOG.md`
8. 更新 `round_state/`
9. 生成 `reports/round_xx_completion_report.md`

## 5) 验证命令

```bash
python scripts/agent_gate.py
python scripts/scan_repos.py --config config/repos.example.yaml --dry-run
python scripts/analyze_repos.py --input data/repo_snapshots.example.json --output data/repo_status.example.json
python scripts/generate_dashboard.py --input data/repo_status.example.json --output dashboard/index.html
```

若命令因示例数据不足无法完整运行，必须在当轮完成报告说明原因与修复计划。
