# Round 01 - Repo Registry

## 目标

- 建立真实 `config/repos.yaml`（从 example 复制并填写）
- 支持手动登记仓库：类型、优先级、标签、状态
- 支持路径校验与 `missing` 标记
- **不**自动扫描整个 `PycharmProjects` 目录

## 不做什么

- 不做全自动仓库发现
- 不读取业务源码
- 不修改被管理仓库
- 不在登记时调用外部 API

## 前置条件

- Round 00 骨架已完成
- 用户已知要管理的仓库路径列表

## 输入文件

- `config/repos.example.yaml`
- `config/managed_files.yaml`

## 输出文件

- `config/repos.yaml`
- `docs/index.md`（登记流程说明，如需）

## 阶段任务

### 阶段 1 — 字段建模

- 定义字段：`name`, `path`, `type`, `priority`, `tags`, `status`, `notes`
- 在 example 中补充注释说明各字段含义

### 阶段 2 — 手动登记

- 用户逐条添加仓库，禁止批量目录扫描
- 路径不存在时标记 `status: missing`

### 阶段 3 — 校验

- `scan_repos.py --config config/repos.yaml --dry-run` 验证清单可读
- 缺失路径在输出中明确列出

## 验收标准

- `config/repos.yaml` 存在且可维护
- 每条记录有 name/path/type/priority
- 缺失路径可标记 `missing`
- dry-run 扫描不报错

## 风险点

- 仓库路径变化导致失效
- 登记过多仓库增加维护成本

## 推荐执行 Agent

- Cursor / Human（路径由 Human 确认）

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
创建 config/repos.yaml，从 repos.example.yaml 复制结构。
手动登记用户指定的仓库，不扫描整个 PycharmProjects。
验证：python3 scripts/scan_repos.py --config config/repos.yaml --dry-run
```

> **状态说明：** 本轮规格已扩写，实际执行延后；Round 1 治理复核轮完成后直接进入 Round 02。
