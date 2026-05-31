# Round 23 - Feishu Hardening

## 目标

- 发送前 20KB 体积校验与截断
- 错误码 19022/19024/11232 友好提示
- 签名校验单元测试
- Automation 文档错开整点限流建议

## 不做什么

- 不接入应用机器人事件订阅
- 不引入 lark SDK

## 验收标准

- `pytest tests/test_feishu_integration.py` PASS（含 sign / truncate）
- `prepare_feishu_payload.py` 支持 LLM 摘要段落
- 文档更新限流与关键词说明

## 推荐执行 Agent

- Cursor

## 可复制给 Cursor 的任务摘要

加固 prepare_feishu_payload：20KB、错误码、签名单测；更新 feishu 文档。
