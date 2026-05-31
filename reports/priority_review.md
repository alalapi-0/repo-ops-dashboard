# Priority Review

- generated_at: 2026-05-31T19:30:45.090215+00:00
- 说明：以下为**建议**优先级；Human 在 `config/repos.yaml` 的 `priority_hint` 中覆盖后，`final_priority` 以人工为准。

## 因素说明
- **income_relevance**: 与工作/收入相关性（由 type 代理）
- **ai_roadmap**: AI 主线相关性（meta_ops / novel / manga 加权）
- **demo_value**: 短期可展示（health_score 代理）
- **reuse**: 组件复用潜力（meta_ops / agent 类加权）
- **cost**: 维护成本（blocker/freeze 扣分）
- **substitute_risk**: 被替代风险（archive/freeze 扣分）

## 仓库建议

### novel-continuation-agent
- 得分: 12
- 建议: low → 最终: **high** (人工覆盖)
- 理由: type=novel_agent (+22); health=44 → demo (+15); blockers (-25)
- Human hint: high

### ai-manga
- 得分: -101
- 建议: low → 最终: **high** (人工覆盖)
- 理由: type=ai_manga (+22); health=8 → demo (+2); blockers (-25); archive_candidate (-100)
- Human hint: high

### repo-ops-dashboard
- 得分: 55
- 建议: high → 最终: **high** (人工覆盖)
- 理由: type=meta_ops (+25); health=88 → demo (+30)
- Human hint: high

### ai-anime-short-factory
- 得分: 13
- 建议: low → 最终: **high** (人工覆盖)
- 理由: type=ai_anime (+20); health=54 → demo (+18); blockers (-25)
- Human hint: high

### wechat-article-scheduler
- 得分: 8
- 建议: low → 最终: **high** (人工覆盖)
- 理由: type=content_scheduler (+18); health=44 → demo (+15); blockers (-25)
- Human hint: high

### light_novel
- 得分: 9
- 建议: low → 最终: **medium** (人工覆盖)
- 理由: type=translation (+12); health=63 → demo (+22); blockers (-25)
- Human hint: medium

### computer_study_plan
- 得分: -25
- 建议: low → 最终: **medium** (人工覆盖)
- 理由: type=study (+5); health=30 → demo (+10); blockers (-25); freeze_candidate (-15)
- Human hint: medium

### world-news-lens
- 得分: -2
- 建议: low → 最终: **medium** (人工覆盖)
- 理由: type=news (+5); health=54 → demo (+18); blockers (-25)
- Human hint: medium

### pixel-world-asset-forge
- 得分: -24
- 建议: low → 最终: **medium** (人工覆盖)
- 理由: type=asset_forge (+5); health=32 → demo (+11); blockers (-25); freeze_candidate (-15)
- Human hint: medium

### agent-experiments
- 得分: -33
- 建议: low → 最终: **low** (人工覆盖)
- 理由: type=experiment (+5); health=8 → demo (+2); blockers (-25); freeze_candidate (-15)
- Human hint: low

### ai-anime-short-factory-external
- 得分: -33
- 建议: low → 最终: **low** (人工覆盖)
- 理由: type=external (+5); health=8 → demo (+2); blockers (-25); freeze_candidate (-15)
- Human hint: low

### api-mini-labs
- 得分: -28
- 建议: low → 最终: **low** (人工覆盖)
- 理由: type=lab (+5); health=20 → demo (+7); blockers (-25); freeze_candidate (-15)
- Human hint: low

### audiobook-cleaner-lab
- 得分: -25
- 建议: low → 最终: **low** (人工覆盖)
- 理由: type=lab (+5); health=30 → demo (+10); blockers (-25); freeze_candidate (-15)
- Human hint: low

### resilient-personal-network
- 得分: -28
- 建议: low → 最终: **low** (人工覆盖)
- 理由: type=utility (+5); health=20 → demo (+7); blockers (-25); freeze_candidate (-15)
- Human hint: low

### tool-mini-labs
- 得分: -28
- 建议: low → 最终: **low** (人工覆盖)
- 理由: type=lab (+5); health=20 → demo (+7); blockers (-25); freeze_candidate (-15)
- Human hint: low

### typing-practice-app
- 得分: -28
- 建议: low → 最终: **low** (人工覆盖)
- 理由: type=utility (+5); health=22 → demo (+7); blockers (-25); freeze_candidate (-15)
- Human hint: low

### youtube_hq_downloader
- 得分: -25
- 建议: low → 最终: **low** (人工覆盖)
- 理由: type=utility (+5); health=30 → demo (+10); blockers (-25); freeze_candidate (-15)
- Human hint: low

## 汇总

- 高优先级: novel-continuation-agent, ai-manga, repo-ops-dashboard, ai-anime-short-factory, wechat-article-scheduler
- 卡点: novel-continuation-agent, ai-manga, ai-anime-short-factory, wechat-article-scheduler, light_novel, computer_study_plan, world-news-lens, pixel-world-asset-forge, agent-experiments, ai-anime-short-factory-external, api-mini-labs, audiobook-cleaner-lab, resilient-personal-network, tool-mini-labs, typing-practice-app, youtube_hq_downloader
- 冻结候选: ai-manga, computer_study_plan, pixel-world-asset-forge, agent-experiments, ai-anime-short-factory-external, api-mini-labs, audiobook-cleaner-lab, resilient-personal-network, tool-mini-labs, typing-practice-app, youtube_hq_downloader
- 归档候选: ai-manga
