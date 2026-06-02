# Round 40 Completion Report — Playwright Dashboard Validation

## 目标

用 Playwright 检查 Dashboard 渲染、console、network 与基础交互。

## 推进内容

- 新增 `config/ui_check_policy.yaml` 与 `governance/ui_check_policy.example.yaml`。
- 新增 `scripts/validate_ui_check_policy.py`。
- `ui_check.py` 增强：console error 监听、network 失败监听、过滤器/复制按钮交互、`--url` 支持本地 HTTP 预览。
- 新增 `tests/test_ui_check.py`；`agent_gate` 与 eval registry 增加 ui_check_policy 验收。

## 验证

```bash
npm run check:mcp
python3 scripts/agent_gate.py
python3 scripts/validate_ui_check_policy.py
.venv/bin/python -m pytest tests/test_ui_check.py -q
./scripts/refresh_status.sh --example --ui-check
# 浏览器：http://127.0.0.1:8765/dashboard/index.html
```

## 浏览器检查

- 页面渲染：治理面板 V2 + repo cards 可见
- Console：无 error
- Network：无失败请求
- 交互：过滤器切换、复制 Prompt 按钮可点击

## 下一轮

Round 41：`round_41_prompt_generator_for_cursor`（根据 task_spec 生成 Cursor Prompt）。
