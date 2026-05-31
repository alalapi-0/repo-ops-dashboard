# Round 02 - Readonly Scanner

## 目标

- 完成 allowlist 只读扫描逻辑
- 生成 `data/repo_snapshots.json`
- 记录 `missing`、`warning`、`skipped`
- 不读取敏感文件（`.env`、密钥等）

## 不做什么

- 不全量递归扫描源码
- 不读取 denylist 文件
- 不写入被管理仓库
- 默认 dry-run，需显式 `--no-dry-run` 才写文件

## 前置条件

- `config/repos.yaml` 或 `repos.example.yaml` 可用
- `config/managed_files.yaml` allowlist/denylist 已配置

## 输入文件

- `config/repos.yaml`
- `config/managed_files.yaml`
- `repo_protocol_standard.yaml`

## 输出文件

- `data/repo_snapshots.json`（非 dry-run 时）
- 扫描日志/警告列表

## 阶段任务

### 阶段 1 — Allowlist 采集

- 按 pattern 读取 README、AGENTS.md、round_state 等
- glob 模式无匹配时记录 warning

### 阶段 2 — Denylist 拦截

- 跳过 `.env`、`node_modules`、密钥文件
- 记录 skipped 原因

### 阶段 3 — 快照输出

- 汇总每仓 `read_files`、`warnings`、`missing`
- 支持 `--output data/repo_snapshots.json`

## 验收标准

- dry-run 可预览扫描结果
- 不读取 denylist 文件
- missing 路径明确标记
- 快照 JSON 可被 analyze_repos 消费

## 风险点

- allowlist pattern 过宽可能误读
- 大文件需 size 限制

## 推荐执行 Agent

- Cursor / Codex

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
完善 scan_repos.py 只读扫描，确保 allowlist/denylist 生效。
验证：python3 scripts/scan_repos.py --config config/repos.example.yaml --dry-run
写快照：python3 scripts/scan_repos.py --config config/repos.example.yaml --no-dry-run --output data/repo_snapshots.json
```
