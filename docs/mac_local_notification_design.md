# Mac 本地通知设计

## 目标

在 macOS 上推送今日建议与 blocker 摘要；默认 dry-run 输出 payload，CI 或非 Darwin 环境不强制 osascript。

## 机器可读资产

| 文件 | 说明 |
|------|------|
| `config/mac_notification_policy.yaml` | 标题、内容来源、delivery 规则 |
| `reports/mac_notification_payload.json` | dry-run / send 前的通知载荷 |
| `reports/mac_notification_plan.md` | 人类可读摘要 |

## 脚本

```bash
python3 scripts/send_mac_notification.py              # dry-run 写 payload
python3 scripts/send_mac_notification.py --send       # macOS 上尝试 osascript
python3 scripts/validate_mac_notification_policy.py
```

## 内容来源

- **今日建议**：`daily_brief.md` 中「短提醒」或「今日最该推进」摘录。
- **Blockers**：`repo_status.json` 中有 blockers 的仓库名（最多 3 条）。

## 安全边界

- 不读取 `.env`；不推送完整本地路径。
- `--send` 仅在 Darwin 且非 CI 时调用 `osascript`；失败时仍保留 payload 文件。
- 默认 `dry_run: true`。

## 验证

```bash
python3 scripts/send_mac_notification.py --status data/repo_status.example.json --write
python3 scripts/agent_gate.py
```
