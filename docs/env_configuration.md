# 环境变量配置

本仓库通过**本地 `.env`** 或 **Cursor Automations Secrets** 注入密钥。扫描/分析脚本**不读取** `.env`；仅 opt-in 脚本在显式开关下读取。

## 快速开始

```bash
cp .env.example .env
# 编辑 .env，填入 OpenRouter / 飞书等密钥（勿提交 git）
```

`.env` 已在 [`.gitignore`](../.gitignore) 中忽略；[`.env.example`](../.env.example) 可安全入库，仅含占位符。

## 变量映射

| 变量 | 用途 | 消费脚本 | 何时需要 |
|------|------|----------|----------|
| `LLM_ENABLED` | 是否允许 LLM 调用 | `generate_llm_summary.py`、`refresh_status.sh --llm-summary` | Round 22+；默认 `false` |
| `LLM_PROVIDER` | 提供商标识 | `generate_llm_summary.py` | 当前仅 `openrouter` |
| `OPENROUTER_API_KEY` | OpenRouter API 密钥 | `generate_llm_summary.py --call` | LLM 真实调用 |
| `OPENROUTER_BASE_URL` | API 根地址 | `generate_llm_summary.py --call` | 默认官方地址 |
| `LLM_MODEL` | 模型 slug | `generate_llm_summary.py --call` | 默认 `deepseek/deepseek-v4-pro`（推理优先，勿用 openai/google/anthropic 默认） |
| `LLM_MAX_TOKENS` | 输出 token 上限 | `generate_llm_summary.py --call` | 可选 |
| `OPENROUTER_HTTP_REFERER` | OpenRouter 归因 | `generate_llm_summary.py --call` | 可选 |
| `OPENROUTER_X_TITLE` | OpenRouter 归因 | `generate_llm_summary.py --call` | 可选 |
| `AUTO_APPROVE_GENERATIONS` | 生成流水线自动通过 | `run_generation_pipeline.py` | 本地 e2e 测试；默认 `false` |
| `REVIEW_MODE` | `manual` / `auto` | `run_generation_pipeline.py` | 生产保持 `manual` |
| `SKIP_HUMAN_REVIEW` | 跳过人工审核门 | `run_generation_pipeline.py` | 与 `REVIEW_MODE=auto` 等效 |
| `FEISHU_WEBHOOK_URL` | 群机器人 Webhook | `prepare_feishu_payload.py --send` | 飞书推送 |
| `FEISHU_SIGN_SECRET` | 机器人签名校验 | `prepare_feishu_payload.py --send` | 飞书启用签名时 |
| `FEISHU_APP_ID` | 开放平台应用 | `sync_feishu_bitable.py --sync` | Bitable 同步 |
| `FEISHU_APP_SECRET` | 开放平台应用 | `sync_feishu_bitable.py --sync` | Bitable 同步 |
| `FEISHU_BITABLE_APP_TOKEN` | 多维表格 app | `sync_feishu_bitable.py --sync` | Bitable 同步 |
| `FEISHU_BITABLE_TABLE_ID` | 数据表 ID | `sync_feishu_bitable.py --sync` | Bitable 同步 |

## LLM 开关关系

1. `.env` 中 `LLM_ENABLED=true`
2. 运行 `./scripts/refresh_status.sh --llm-summary --call` 或 `python3 scripts/generate_llm_summary.py --call`

默认 **dry-run**：只写占位 Markdown，不联网。与 [`AGENTS.md`](../AGENTS.md) 一致：无 Human opt-in 不调用外部 API。

### 生成流水线（auto-approve 测试模式）

`scripts/run_generation_pipeline.py` 在 `--call` 下发起真实 OpenRouter 请求，写入 `data/generations/`（pending → approved → library），并更新 `index.json`。

```bash
# 本地 e2e（需 LLM_ENABLED=true 与有效 OPENROUTER_API_KEY）
AUTO_APPROVE_GENERATIONS=true REVIEW_MODE=auto SKIP_HUMAN_REVIEW=true \
  LLM_ENABLED=true python3 scripts/run_generation_pipeline.py \
  --call --auto-approve --review-mode auto --skip-human-review --round round_1

python3 scripts/generate_generations_page.py
```

切回人工审核：省略 `--auto-approve`，或设 `REVIEW_MODE=manual`、`AUTO_APPROVE_GENERATIONS=false`。生成结果留在 `data/generations/pending/` 等待人工处理。

`refresh_status.sh --generation-pipeline --call` 在 `LLM_ENABLED=true` 时运行同上流水线并刷新 `dashboard/generations.html`。

### OpenRouter 401「User not found」

该错误出现在 **认证阶段**（`Authorization: Bearer`），与 `model` 参数无关；错误模型通常返回 4xx 且提示模型不可用，而非 401 User not found。常见原因：密钥过期/无效、误用 Management API Key、或 `.env` 未加载。请在 [OpenRouter Keys](https://openrouter.ai/settings/keys) 新建以 `sk-or-` 开头的 API Key，并确认 `.env` 中 `LLM_MODEL` 与示例一致（默认 `deepseek/deepseek-v4-pro`）。

## Cursor Automations Secrets

在 Automation 的 Secrets 中注入与 `.env` 相同的键名即可。推荐命令见 [`cursor_automation_guide.md`](cursor_automation_guide.md)。

若 Automation 环境无法 source `.env`，飞书可单独用：

```bash
./scripts/feishu_send.sh --send
```

## 安全原则

- 禁止将真实密钥写入 git、日志或 Dashboard
- `feishu_send.sh` 会在存在时 `source` 根目录 `.env`（不打印变量值）
- `agent_gate.py` 检查 `.env` 未被 git 跟踪
- 扫描 denylist 含 `.env`（不读取被管理仓库的密钥文件）

## 相关文档

- 安装：[`installation.md`](installation.md)
- 飞书：[`feishu_integration_plan.md`](feishu_integration_plan.md)
- 调度：[`cursor_automation_guide.md`](cursor_automation_guide.md)
- 远期路线：[`personal_os_roadmap.md`](personal_os_roadmap.md)
