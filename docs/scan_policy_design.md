# Scan Policy Design

`config/scan_policy.yaml` 定义只读扫描器的 v2 核心治理分类，与 `config/managed_files.yaml` 的 allowlist/denylist 配合使用。

## 核心分类

| 分类 | 典型 pattern | 是否必需 |
|------|-------------|---------|
| readme | `README.md`, `README.*` | 是 |
| agents | `AGENTS.md` | 是 |
| protocol | `repo_protocol_standard.yaml` | 是 |
| round_state | `round_state/**` | 否 |

## 安全边界

- 默认 `--dry-run`；仅 `--no-dry-run` 写快照。
- 不读取 `.env`、密钥、token；denylist 在 `managed_files.yaml`。
- 不做 `rglob` / `os.walk` 全量遍历；仅按 allowlist pattern 采集。
- 不修改被管理业务仓库。

## 脚本

- `scripts/validate_scan_policy.py`：校验 policy 结构与 v2 标记。
- `scripts/read_scan_policy.py`：读取并摘要 policy。
- `scripts/scan_repos.py`：输出 `scanner_version`、`core_governance`、`file_categories`。

## 快照字段（v2）

每个 repo 行新增：

- `file_categories`：按核心分类归类的已读文件。
- `core_governance`：`found_categories`、`missing_required_categories`、`required_coverage_pct`。
