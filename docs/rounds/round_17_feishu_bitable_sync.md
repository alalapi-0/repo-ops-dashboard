# Round 17 - Feishu Bitable Sync

## 目标

- 定义多维表格字段 schema
- `sync_feishu_bitable.py` 从 `repo_status.json` 幂等 upsert
- 与 Cursor Automations 串联 `--bitable-sync`

## 不做什么

- 不同步本地绝对路径
- 不引入 `lark_oapi` SDK
- 默认 dry-run，不自动 `--sync`

## 前置条件

- Round 16 飞书群推送文档就绪
- Human 创建飞书 Base 与开放平台应用

## 输入文件

- `data/repo_status.json`

## 输出文件

- `scripts/sync_feishu_bitable.py`
- `docs/feishu_bitable_schema.md`
- 更新的 `.env.example`、`refresh_status.sh`

## 验收标准

- dry-run 打印各仓摘要
- `--sync` 需四套 FEISHU_* env
- `refresh_status.sh --bitable-sync` 调用 sync 脚本
- 无 path 字段写入 Bitable

## 推荐执行 Agent

- Cursor（脚本）/ Human（飞书应用与表结构）

## 可复制给 Cursor/Codex/OpenClaw 的任务摘要

```
实现 sync_feishu_bitable.py（stdlib API，dry-run 默认）。
文档 feishu_bitable_schema.md。refresh_status.sh 增加 --bitable-sync。
```
