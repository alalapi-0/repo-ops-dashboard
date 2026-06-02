# 安装与日常运行

## 依赖

```bash
cd /path/to/repo-ops-dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # Playwright（可选）
python3 -m playwright install chromium
```

## 登记仓库

1. 编辑 [`config/repos.yaml`](../config/repos.yaml)，或从 example 复制。
2. 合并新目录：`python3 scripts/sync_repo_registry.py --workspace /Users/alalapi/PycharmProjects`
3. 同步治理登记：`python3 scripts/sync_project_registry.py`（`--dry-run` 仅校验）
4. 同步组合快照：`python3 scripts/sync_portfolio_state.py`（依赖 registry + repo status JSON）

## 一条命令刷新

**示例数据（CI / 新 Agent 验证）：**

```bash
./scripts/refresh_status.sh --example --ui-check
python3 -m pytest
```

**真实登记仓库：**

```bash
./scripts/refresh_status.sh --ui-check
```

或逐步执行：

```bash
python3 scripts/agent_gate.py
python3 scripts/scan_repos.py --config config/repos.yaml --no-dry-run
python3 scripts/analyze_repos.py
python3 scripts/generate_dashboard.py
python3 scripts/generate_report.py
python3 scripts/prepare_feishu_payload.py
python3 scripts/ui_check.py --file dashboard/index.html --screenshot reports/ui_screenshots/dashboard.png --headless true
python3 -m pytest
```

在浏览器打开 `dashboard/index.html`（`file://`）。

## 配置环境变量（可选）

1. 复制模板：`cp .env.example .env`
2. 按需填入 OpenRouter、飞书等密钥（见 [`env_configuration.md`](env_configuration.md)）
3. **默认不调用外部 API**；LLM 与飞书发送均需显式 opt-in 开关

## Feishu（可选）

见 [`feishu_integration_plan.md`](feishu_integration_plan.md)：配置 `FEISHU_WEBHOOK_URL` 后执行 `prepare_feishu_payload.py --send`。

## 故障排查

| 问题 | 处理 |
|------|------|
| `Config not found` | 创建 `config/repos.yaml` 或指定 `--config` |
| Playwright 未安装 | `pip install -r requirements-dev.txt && python3 -m playwright install chromium` |
| 某仓库显示 archived | 路径缺失或目录为空，见 [`lifecycle_rules.md`](lifecycle_rules.md) |
| Human 笔记不显示 | 复制 `data/human_notes.example.json` → `data/human_notes.json` 并编辑 |

## 文档索引

- 环境变量：[`env_configuration.md`](env_configuration.md)
- 架构：[`architecture.md`](architecture.md)
- 生命周期：[`lifecycle_rules.md`](lifecycle_rules.md)
- 下游集成：[`downstream_integrations.md`](downstream_integrations.md)
- 调度：[`scheduler.md`](scheduler.md)
