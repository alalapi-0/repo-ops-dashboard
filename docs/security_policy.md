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

- 仓库策略和脚本参数不授予执行或写入权限；任何副作用仍需当前用户与上层策略授权。
- 普通检查和 dry-run 默认只读。
- `scripts/agent_gate.py` 默认只读并返回 0/1/2；仅在已有写入权限时显式使用 `--write-report`。
- Round 0 禁止外部 API 调用。

## 审计策略

- 仅已授权启动或推进的产品轮次才输出 completion report。
- 在报告中写明是否读取密钥、是否调用外部 API、是否修改被管理仓库。
