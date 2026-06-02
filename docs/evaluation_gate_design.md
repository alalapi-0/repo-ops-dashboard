# Evaluation Gate 设计

Eval gate 是治理轮的验收入口。它不追求一次性完美，而是把每轮最低安全线和质量线显式化。

## 原则

- 每轮至少通过基础 gate。
- 失败项进入 blocker 或 review_queue。
- schema、路径、协议、安全边界优先脚本化。
- Dashboard UI 检查属于本地可选但推荐的浏览器级验证。

## 当前注册表

基础 eval 定义在 `governance/evals/registry.yaml`，包括协议、AGENTS、密钥暴露、只读边界、Dashboard、round_state、completion report、task_spec、proof_of_work、Playwright 检查。

Round 46 起由 `scripts/run_eval_registry.py` 按 registry 条目脚本化执行（默认 dry-run，跳过 ui_check 子进程）。

## 后续

Round 47 起可把 handoff_packet 与 failure recovery 条目纳入 registry runner。
