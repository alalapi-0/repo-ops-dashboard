# Round 00 - Bootstrap

## 目标

- 创建仓库骨架
- 创建通用协议
- 创建 `AGENTS.md`
- 创建 Cursor Rules
- 创建基础脚本骨架
- 创建静态 Dashboard 示例
- 创建后续 Round 文档

## 不做什么

- 不接 OpenClaw/Feishu 实际 API
- 不修改被管理业务仓库
- 不全量扫描业务仓源码

## 输入文件

- `repo_protocol_standard.yaml`
- `AGENTS.md`
- `config/*.yaml`

## 输出文件

- `scripts/*.py`
- `dashboard/*`
- `docs/rounds/*`
- `round_state/current_round.yaml`
- `reports/round_00_completion_report.md`

## 具体阶段

1. 骨架初始化
2. 治理文件落地
3. 脚本骨架实现
4. 静态页面与报告输出
5. 验证与收尾

## 验收标准

- 核心结构完整可运行
- 指定命令可执行或有明确失败说明
- 无密钥读取、无外部 API、无业务仓写入

## 风险

- 示例数据与真实仓库状态可能偏差
- 规则初版可能需后续轮次细化

## 推荐执行 Agent

- Cursor
