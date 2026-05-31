# Round 19 - Local Imports Optional (ICS / CSV)

## 目标

- 从本地配置路径只读读取日历 ICS、财务 CSV 摘要
- 并入 weekly_review，无外部 API
- 路径为空时优雅跳过

## 不做什么

- 不下载远程 ICS/CSV
- 不写入导入源文件
- 不解析复杂 iCal 扩展字段

## 前置条件

- Round 18 weekly_review 可用

## 输入文件

- `config/local_imports.yaml`（Human 本地，gitignore）
- `config/local_imports.example.yaml`

## 输出文件

- weekly_review 中「本地导入摘要」段落

## 阶段任务

### 阶段 1 — 配置

- example yaml 含 calendar_ics / finance_csv 路径

### 阶段 2 — 读取脚本

- `scripts/read_local_imports.py` 输出 Markdown 片段

### 阶段 3 — 合并

- `generate_weekly_review.py --imports-config`

## 验收标准

- 无配置或文件缺失时不报错
- 示例 ICS/CSV 可生成摘要
- pytest / agent_gate PASS

## 风险点

- ICS 格式多样；仅做轻量 SUMMARY 提取

## 推荐执行 Agent

- Cursor

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
实现 read_local_imports.py，从 local_imports.yaml 路径只读 ICS/CSV 摘要，并入 weekly_review。
```
