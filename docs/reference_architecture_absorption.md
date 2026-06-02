# 参考架构吸收

本项目只吸收参考仓库的方法论，不复制源码，不引入重型框架，不把 repo-ops-dashboard 变成第三个编程 Agent。

## 从 MetaGPT 吸收什么

- SOP：把项目治理拆成可复用流程，而不是每次靠临场发挥。
- Team serialization：把角色、任务、状态、交接写成可恢复结构。
- budget / cost manager：未来将预算、模型成本、API 使用作为组合治理输入。
- role assignment：明确 Cursor、Codex、OpenClaw、业务 Agent 与 HumanOwner 的边界。
- 落地方式：只取思想，不复制重型框架。

## 从 LangGraph 吸收什么

- checkpoint：关键状态要能快照，后续用于恢复与复盘。
- interrupt / HITL：高风险动作进入 review_queue。
- pending writes：待写入、待发布、待同步应显式排队。
- failure recovery：失败分类、重试次数、升级路径应可记录。

## 从 Codex 吸收什么

- rollout.jsonl：每次执行留下事件流。
- execpolicy：执行边界必须显式化。
- cwd 绑定：每个任务和 handoff 必须绑定工作目录。
- confirmation policy：高风险命令或写入要确认。
- audit trail：能追踪计划、命令、文件变化、验证与 proof。

## 从 OpenHands 吸收什么

- sandbox：执行环境边界优先于智能程度。
- agent memory approval：长期记忆、skill、playbook 推广需要人工批准。
- repository microagents：每个仓库未来可有轻量上下文入口，而不是全量读仓库。
- remote run 思想：后续可以远程执行，但必须先有审计和策略。

## 从 RepoAgent 吸收什么

- repo_context_index：用低 token 摘要作为默认入口。
- git diff 驱动文档更新：后续根据变更提示文档同步。
- 防止全仓库上下文爆炸：只读管理文件和索引，不读业务源码全文。

## 从 evals 吸收什么

- eval registry：把验收项注册为可运行或可检查条目。
- gate：每轮至少通过基础 gate。
- schema validation：task_spec、proof_of_work、handoff_packet 要逐步脚本化校验。
- threshold：不是所有 eval 都一票否决，需区分 required 与 advisory。

## 从 openai-agents-js / software-agent-sdk 吸收什么

- handoff：治理层输出结构化交接包。
- structured output：任务、proof、状态用 YAML/JSON。
- guardrail：边界、确认、权限、denylist 是协议的一部分。
- todo/task intake：任务入口标准化。
- event log：运行事件可审计、可复盘。

## 落地原则

- 先协议，后自动化。
- 先 YAML/JSON，后 UI。
- 先人工确认，后自动执行。
- 先本地报告，后通知系统。
- 先 repo-ops-dashboard 内部实现，后接 OpenClaw。
