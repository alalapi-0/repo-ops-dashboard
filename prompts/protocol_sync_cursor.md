# Cursor — 协议同步：{{repo_name}}

你是 Cursor，在**目标业务仓库** `{{repo_name}}` 内工作（非 repo-ops-dashboard）。

## 当前差异

- 缺失治理文件：{{missing_governance}}
- 已有治理文件：{{present_governance}}
- 参考协议版本：{{protocol_version}}

## 任务

1. 只读对比本仓与 repo-ops-dashboard 的 `repo_protocol_standard.yaml` 结构。
2. 补齐缺失的 `AGENTS.md` / `README.md` / `round_state/` / `docs/index.md`（按仓类型裁剪，勿照搬无关 Round）。
3. **禁止**读取 `.env`、禁止批量删除、禁止自动 git commit。

## 验收

- 缺失项减少；变更仅限治理文件 allowlist 内。
- 输出 `docs/reports/repo_protocol_sync_report.md` 说明做了什么。
