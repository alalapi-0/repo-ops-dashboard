# Execpolicy 设计

当前 `governance/execpolicy/` 是文档级约束，用于把执行边界显式化。它不是系统沙箱，也不能替代操作系统权限。

## 当前作用

- 说明哪些路径可读、可写、必须确认或禁止。
- 指导 Cursor/Codex/OpenClaw 的 handoff_packet。
- 为 `agent_gate.py` 后续脚本化检查提供规则来源。

## 后续脚本化

- `scripts/validate_execpolicy.py`：解析并校验 `.rules` 语法与 portfolio 必选约束。
- `scripts/read_execpolicy.py`：读取规则摘要；`--all` 校验整个 `governance/execpolicy/`。
- `scripts/check_execpolicy_action.py`：对路径或命令做 dry-run 分类（allow/deny/prompt/unknown）。
- `agent_gate.py` 的 `execpolicy` 检查调用上述校验。
- 高风险命令必须进入 `review_queue`。
- 可逐步引入结构化 YAML 规则，替代当前伪规则文本。

## 高风险示例

- `git push`
- `rm -rf`
- `launchctl`
- `curl ... | bash`
- 写入被管理业务仓库
- 修改通用协议、execpolicy、长期 skill/playbook
