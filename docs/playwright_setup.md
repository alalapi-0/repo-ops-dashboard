# Playwright 安装与使用

## 安装方式

```bash
pip install -r requirements-dev.txt
python3 -m playwright install chromium
```

生产依赖（扫描/分析/报告）只需：

```bash
pip install -r requirements.txt
```

## 用途

Playwright 用于让 Cursor Agent **看见**本地 Dashboard 页面并做 UI 检查：

- 打开 `dashboard/index.html`（`file://` 协议）
- 截图保存到 `reports/ui_screenshots/`
- 检查页面标题是否包含 `Repo Ops Dashboard`
- 检查 dashboard 容器是否存在
- 检查仓库卡片（`.repo-card`）是否渲染
- 检查优先级标签、推荐 Agent 等字段
- 检查错误/警告信息

运行命令：

```bash
python3 scripts/ui_check.py \
  --file dashboard/index.html \
  --screenshot reports/ui_screenshots/dashboard.png \
  --headless true
```

报告输出：`reports/ui_check_report.md`

## 安全边界

- **不登录**任何网站
- **不访问**外部业务系统
- **不读取**浏览器账号
- **不进行**支付、社交、邮箱相关操作
- **不访问**真实通知平台
- **不上传**截图到外部服务
- Playwright 失败不影响核心扫描脚本

## 未安装时的提示

若 Playwright 尚未安装，`ui_check.py` 会输出：

```
Please run:
pip install -r requirements-dev.txt
python3 -m playwright install chromium
```

并退出码 2，不影响其他脚本。
