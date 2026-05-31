# 安全策略

## 绝对边界

- 不读取 `.env`、密钥、Token、证书文件。
- 不修改被管理业务仓库。
- 不自动提交业务仓库。
- 不全量扫描 `~/PycharmProjects`。

## 读取策略

- 仅允许读取 allowlist 管理文件。
- 若配置请求了 allowlist 之外文件，脚本必须跳过并记录 warning。
- denylist 命中即跳过，不得读取。

## 执行策略

- 所有脚本默认 dry-run 或只在本仓库产物输出目录写文件。
- `scripts/agent_gate.py` 为推进前检查门，返回 0/1/2。
- Round 0 禁止外部 API 调用。

## 审计策略

- 每轮输出 completion report。
- 在报告中写明是否读取密钥、是否调用外部 API、是否修改被管理仓库。
