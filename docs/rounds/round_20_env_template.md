# Round 20 - Environment Template & Configuration Docs

## 目标

- 修复 `.env.example` 无法入库（`.gitignore` 误伤）
- 扩展 OpenRouter + Feishu 环境变量模板
- 新增配置文档，说明 opt-in 与脚本映射

## 不做什么

- 不实现 LLM 调用（Round 22）
- 不读取被管理业务仓 `.env`

## 验收标准

- `python3 scripts/agent_gate.py` PASS
- `.env.example` 可被 `git add`
- `docs/env_configuration.md` 完整

## 推荐执行 Agent

- Cursor（文档与模板）

## 可复制给 Cursor 的任务摘要

修复 .gitignore 放行 .env.example；扩展 OpenRouter/Feishu 模板；写 env_configuration.md。
