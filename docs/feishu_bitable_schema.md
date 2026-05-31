# 飞书多维表格（Bitable）字段设计（Round 17）

将 [`data/repo_status.json`](../data/repo_status.example.json) 中每个仓库一行 upsert 到飞书多维表格。**不同步** `path` 等本地绝对路径。

## Human 一次性配置

1. 在飞书创建 **多维表格 Base**，新建数据表（建议表名 `repo_status`）。
2. 在 [飞书开放平台](https://open.feishu.cn/) 创建 **企业自建应用**。
3. 为应用开通权限（至少）：
   - `bitable:app` — 读写多维表格
   - 或按控制台提示勾选「查看、编辑和管理多维表格」
4. 将应用添加为 Base 的 **协作者**（可编辑）。
5. 从 Base URL 获取 `app_token`，从表设置获取 `table_id`。
6. 在本机 `.env` 填入（见 [`.env.example`](../.env.example)）：
   - `FEISHU_APP_ID`
   - `FEISHU_APP_SECRET`
   - `FEISHU_BITABLE_APP_TOKEN`
   - `FEISHU_BITABLE_TABLE_ID`

## 列定义（字段名须与下表一致）

| 字段名 | 飞书列类型 | 说明 | 来源 |
|--------|-----------|------|------|
| `repo_name` | 文本 | **逻辑主键**，仓库登记名 | `repos[].name` |
| `type` | 单选 | 项目类型 | `type` |
| `priority` | 单选 | 优先级 | `priority` |
| `health_score` | 数字 | 健康分 0–100 | `health_score` |
| `lifecycle_status` | 单选 | 生命周期 | `lifecycle_status` |
| `blockers` | 多行文本 | 卡点列表 | `blockers` 用 `; ` 拼接 |
| `recommended_agent` | 单选 | 建议 Agent | `recommended_agent` |
| `next_actions` | 多行文本 | 下一步 | `next_actions` 用 `; ` 拼接 |
| `last_checked` | 日期 | 上次扫描 | `last_checked` ISO → 毫秒时间戳 |
| `sync_at` | 日期 | 本次同步时间 | 脚本写入 UTC |

### 单选列建议选项

创建列后，在飞书 UI 中为单选列预置选项（脚本写入的值须匹配）：

- **type**：与 `config/repos.yaml` 中 `type` 一致（如 `translation`、`meta_ops` 等）
- **priority**：`high` / `medium` / `low`
- **lifecycle_status**：`active` / `freeze_candidate` / `archived` 等
- **recommended_agent**：`Cursor` / `Codex` / `Human` / `OpenClaw`

若选项不存在，飞书 API 可能拒绝写入；可先 dry-run 再在 UI 中补选项。

## 同步脚本

```bash
# 默认 dry-run：打印将 upsert 的行摘要，不调用 API
python3 scripts/sync_feishu_bitable.py --input data/repo_status.example.json

# 显式写入（需 .env 凭证）
python3 scripts/sync_feishu_bitable.py --input data/repo_status.json --sync
```

幂等逻辑：按 `repo_name` 查已有记录 → 有则 update，无则 create。

## 与 Cursor Automations 串联

在 [`cursor_automation_feishu.md`](cursor_automation_feishu.md) 的 refresh 命令后追加 `--bitable-sync`：

```bash
./scripts/refresh_status.sh --feishu-send --bitable-sync
```

## 安全

- App Secret / token 仅环境变量，禁止入库。
- 记录中不得出现 `/Users/...` 完整路径。
- 默认 dry-run；`--sync` 为 opt-in。
