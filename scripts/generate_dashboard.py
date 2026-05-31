#!/usr/bin/env python3
"""Generate static dashboard HTML from repository status data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def esc(text: Any) -> str:
    value = str(text)
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def render_card(repo: dict[str, Any]) -> str:
    blockers = repo.get("blockers", []) or ["无"]
    next_actions = repo.get("next_actions", []) or ["无"]
    badges: list[str] = []
    if repo.get("freeze_candidate"):
        badges.append('<span class="badge freeze">Freeze</span>')
    if repo.get("archive_candidate"):
        badges.append('<span class="badge archive">Archive</span>')

    return f"""
    <article class="repo-card">
      <div class="card-head">
        <h3>{esc(repo.get("name"))}</h3>
        <div>{''.join(badges)}</div>
      </div>
      <p><strong>类型:</strong> {esc(repo.get("type"))}</p>
      <p><strong>状态:</strong> {esc(repo.get("status"))}</p>
      <p><strong>阶段:</strong> {esc(repo.get("current_stage"))}</p>
      <p><strong>优先级:</strong> {esc(repo.get("priority"))}</p>
      <p><strong>健康分:</strong> {esc(repo.get("health_score"))}</p>
      <p><strong>推荐 Agent:</strong> {esc(repo.get("recommended_agent"))}</p>
      <p><strong>卡点:</strong> {esc('; '.join(blockers))}</p>
      <p><strong>下一步:</strong> {esc('; '.join(next_actions))}</p>
    </article>
    """


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate static dashboard html")
    parser.add_argument("--input", default="data/repo_status.json", help="Input status json")
    parser.add_argument("--output", default="dashboard/index.html", help="Output html path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    payload = load_json(input_path)
    repos = list(payload.get("repos", []))
    high_count = sum(1 for r in repos if r.get("priority") == "high")
    blocked_count = sum(1 for r in repos if r.get("blockers"))
    freeze_count = sum(1 for r in repos if r.get("freeze_candidate"))
    now_text = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    cards = "\n".join(render_card(repo) for repo in repos)

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Repo Ops Dashboard</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <main class="container">
    <header>
      <h1>Repo Ops Dashboard</h1>
      <p>更新时间：{esc(now_text)}</p>
    </header>
    <section class="stats">
      <div class="stat"><span>总仓库数</span><strong>{len(repos)}</strong></div>
      <div class="stat"><span>高优先级</span><strong>{high_count}</strong></div>
      <div class="stat"><span>卡住仓库</span><strong>{blocked_count}</strong></div>
      <div class="stat"><span>冻结候选</span><strong>{freeze_count}</strong></div>
    </section>
    <section class="cards">
      {cards}
    </section>
  </main>
  <script src="app.js"></script>
</body>
</html>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"[ok] dashboard generated: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
