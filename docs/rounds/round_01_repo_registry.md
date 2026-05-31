# Round 01 - Repo Registry

## 目标

- 完善 `config/repos.yaml`
- 支持用户手动登记仓库
- 支持仓库类型、优先级、标签
- 不自动扫描整个 `PycharmProjects`

## 不做什么

- 不做全自动仓库发现
- 不读取业务源码

## 输入文件

- `config/repos.example.yaml`
- `config/managed_files.yaml`

## 输出文件

- `config/repos.yaml`
- `docs/index.md`（如需更新）

## 具体阶段

1. 字段建模
2. 手动登记流程说明
3. 校验规则补充

## 验收标准

- 可维护仓库清单
- 缺失路径可标记 `missing`

## 风险

- 仓库路径变化导致失效

## 推荐执行 Agent

- Cursor / Codex
