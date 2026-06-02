# Feishu/Lark 通知规划报告

- 生成时间: 2026-06-02T17:57:33.043439+00:00
- 模式: planning_only（未调用外部 API）
- 来源就绪: 6/6

## 排期建议

- **日报**: cron `5 9 * * 1-5` · Repo Ops 日报摘要
- **周报**: cron `10 17 * * 5` · Repo Ops 周报摘要

## 来源文件状态

- ✓ `reports/daily_repo_report.md` (2806 bytes)
- ✓ `reports/weekly_repo_report.md` (2807 bytes)
- ✓ `reports/daily_brief.md` (1857 bytes)
- ✓ `data/repo_status.json` (14608 bytes)
- ✓ `reports/llm_daily_summary.md` (375 bytes)
- ✓ `reports/feishu_outbound_preview.json` (1786 bytes)

## 下一步

- HumanOwner 审阅 review_queue 中 feishu 日报权限项
- 配置 FEISHU_WEBHOOK_URL 后使用 send_feishu_notification.py --send
- refresh_status.sh 默认仅生成预览，不加 --feishu-send
