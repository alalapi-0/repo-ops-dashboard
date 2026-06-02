# Analyzer Policy Design

`config/analyzer_policy.yaml` 定义状态分析器 v2 如何从 registry、snapshot 与 round_state 计算健康度维度。

## 输入

| 来源 | 路径 | 用途 |
|------|------|------|
| snapshot | `data/repo_snapshots.json` | 治理文件、`core_governance` |
| registry | `governance/project_registry.yaml` | 项目登记、lifecycle、治理级别 |
| round_state | `round_state/current_round.yaml`（只读，仅当 snapshot 已采集） | 当前轮次与 next_round |

## 健康度维度

| 维度 | 默认权重 | 说明 |
|------|---------|------|
| governance_files | 40 | 核心治理文件覆盖率 |
| registry_alignment | 30 | registry 匹配与 lifecycle 一致性 |
| round_progress | 30 | round_state 进度（completed / in_progress） |

`health_dimensions.composite_score` 为加权合成；最终 `health_score` 与 legacy 规则分取平均（registry 匹配时）。

## 安全边界

- 仅读取 allowlist 内的 `round_state/current_round.yaml`；不读 `.env` 或源码。
- 不修改被管理业务仓库。
- round_state 文件大小上限 64KB。

## 脚本

- `scripts/validate_analyzer_policy.py`
- `scripts/read_analyzer_policy.py`
- `scripts/analyze_repos.py`：输出 `analyzer_version`、`project_id`、`health_dimensions` 等 v2 字段。
