# Round 02 - Readonly Scanner

## 目标

- 完成只读扫描器
- 严格 allowlist
- 输出 `repo_snapshots.json`
- 增加扫描报告

## 不做什么

- 不全量递归源码扫描
- 不写入被管理仓库

## 输入文件

- `config/repos.yaml`
- `config/managed_files.yaml`

## 输出文件

- `data/repo_snapshots.json`
- `reports/scanner_report.md`

## 具体阶段

1. 配置读取
2. 安全过滤
3. 快照输出
4. 报告生成

## 验收标准

- denylist 命中即跳过
- missing 仓库不阻断流程

## 风险

- glob 与路径兼容性问题

## 推荐执行 Agent

- Codex
