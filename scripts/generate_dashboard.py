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


def build_prompt(repo: dict[str, Any]) -> str:
    name = repo.get("name", "unknown")
    agent = repo.get("recommended_agent", "Cursor")
    blockers = repo.get("blockers") or ["无"]
    next_actions = repo.get("next_actions") or ["无"]
    return (
        f"你是 {agent}，请推进仓库 `{name}`。\n\n"
        f"卡点：{'; '.join(blockers)}\n"
        f"下一步：{'; '.join(next_actions)}\n\n"
        "约束：不读取 .env、不修改被管理业务仓库、默认 dry-run。"
    )


def render_card(repo: dict[str, Any], fallback_checked: str, priority_meta: dict[str, Any] | None = None) -> str:
    blockers = repo.get("blockers", []) or ["无"]
    next_actions = repo.get("next_actions", []) or ["无"]
    lifecycle = repo.get("lifecycle_status") or repo.get("status") or "unknown"
    last_checked = repo.get("last_checked") or fallback_checked
    prompt_text = build_prompt(repo)
    badges: list[str] = []
    if repo.get("freeze_candidate"):
        badges.append('<span class="badge freeze">Freeze</span>')
    if repo.get("archive_candidate"):
        badges.append('<span class="badge archive">Archive</span>')

    name = str(repo.get("name", ""))
    priority_source_line = ""
    if priority_meta:
        src = priority_meta.get("priority_source", "")
        label = "人工覆盖" if src == "human_override" else "算法建议"
        final = priority_meta.get("final_priority", repo.get("priority"))
        priority_source_line = f'<p><strong>优先级来源:</strong> {esc(label)} (final={esc(final)})</p>'

    return f"""
    <article class="repo-card" data-priority="{esc(repo.get('priority', ''))}" data-lifecycle="{esc(lifecycle)}" data-agent="{esc(repo.get('recommended_agent', ''))}">
      <div class="card-head">
        <h3>{esc(repo.get("name"))}</h3>
        <div>{''.join(badges)}</div>
      </div>
      <p><strong>类型:</strong> {esc(repo.get("type"))}</p>
      <p><strong>生命周期:</strong> {esc(lifecycle)}</p>
      <p><strong>阶段:</strong> {esc(repo.get("current_stage"))}</p>
      <p><strong>优先级:</strong> {esc(repo.get("priority"))}</p>
      {priority_source_line}
      <p><strong>健康分:</strong> {esc(repo.get("health_score"))}</p>
      <p><strong>治理评分:</strong> {esc(repo.get("priority_score", "—"))} ({esc(repo.get("priority_score_band", ""))})</p>
      <p><strong>推荐 Agent:</strong> {esc(repo.get("recommended_agent"))}</p>
      <p><strong>最后检查:</strong> {esc(last_checked)}</p>
      <p><strong>卡点:</strong> {esc('; '.join(blockers))}</p>
      <p><strong>下一步:</strong> {esc('; '.join(next_actions))}</p>
      <button type="button" class="copy-prompt" data-prompt="{esc(prompt_text)}">复制 Prompt</button>
    </article>
    """


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate static dashboard html")
    parser.add_argument("--input", default="data/repo_status.json", help="Input status json")
    parser.add_argument("--output", default="dashboard/index.html", help="Output html path")
    parser.add_argument(
        "--priority-board",
        default="",
        help="Optional priority board JSON (default: data/priority_board.json if exists)",
    )
    parser.add_argument(
        "--human-notes",
        default="",
        help="Human notes JSON (default: data/human_notes.json or example)",
    )
    return parser.parse_args()


def load_priority_index(board_path: Path) -> dict[str, dict[str, Any]]:
    if not board_path.exists():
        return {}
    board = load_json(board_path)
    return {str(row.get("name", "")): row for row in board.get("repos", [])}


def load_human_notes(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return load_json(path)


def render_human_notes_section(notes: dict[str, Any]) -> str:
    if not notes:
        return ""
    items = "".join(f"<li>{esc(item)}</li>" for item in notes.get("notes", []))
    focus = notes.get("focus_repos", [])
    focus_html = ""
    if focus:
        tags = "".join(f'<span class="note-tag">{esc(name)}</span>' for name in focus)
        focus_html = f'<p class="human-notes-focus">{tags}</p>'
    return f"""
    <section class="human-notes" data-human-notes-ready="true">
      <h2>本周 Human 笔记</h2>
      <p class="human-notes-meta">周次：{esc(notes.get("week_label", "—"))} · 更新：{esc(notes.get("updated_at", "—"))}</p>
      <ul>{items}</ul>
      {focus_html}
    </section>
    """


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    board_path = Path(args.priority_board) if args.priority_board else Path("data/priority_board.json")
    priority_index = load_priority_index(board_path)

    notes_path = Path(args.human_notes) if args.human_notes else Path("data/human_notes.json")
    if not notes_path.exists():
        notes_path = Path("data/human_notes.example.json")
    human_notes_html = render_human_notes_section(load_human_notes(notes_path))

    payload = load_json(input_path)
    repos = list(payload.get("repos", []))
    high_count = sum(1 for r in repos if r.get("priority") == "high")
    blocked_count = sum(1 for r in repos if r.get("blockers"))
    freeze_count = sum(1 for r in repos if r.get("freeze_candidate"))
    archive_count = sum(1 for r in repos if r.get("archive_candidate"))
    generated_at = payload.get("generated_at", "")
    now_text = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    cards = "\n".join(
        render_card(repo, generated_at or now_text, priority_index.get(str(repo.get("name", ""))))
        for repo in repos
    )

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Repo Ops Dashboard</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <main class="container" data-dashboard-ready="true">
    <header>
      <h1>Repo Ops Dashboard</h1>
      <p>更新时间：{esc(now_text)}</p>
    </header>
    <section class="stats">
      <div class="stat"><span>总仓库数</span><strong>{len(repos)}</strong></div>
      <div class="stat"><span>高优先级</span><strong>{high_count}</strong></div>
      <div class="stat"><span>卡住仓库</span><strong>{blocked_count}</strong></div>
      <div class="stat"><span>冻结候选</span><strong>{freeze_count}</strong></div>
      <div class="stat"><span>归档候选</span><strong>{archive_count}</strong></div>
    </section>
    {human_notes_html}
    <section class="filters">
      <label>优先级
        <select id="filter-priority">
          <option value="all">全部</option>
          <option value="high">高</option>
          <option value="medium">中</option>
          <option value="low">低</option>
        </select>
      </label>
      <label>生命周期
        <select id="filter-lifecycle">
          <option value="all">全部</option>
          <option value="active">active</option>
          <option value="bootstrap">bootstrap</option>
          <option value="missing">missing</option>
          <option value="empty">empty</option>
          <option value="archived">archived</option>
          <option value="freeze_candidate">freeze_candidate</option>
          <option value="archive_candidate">archive_candidate</option>
        </select>
      </label>
      <label>推荐 Agent
        <select id="filter-agent">
          <option value="all">全部</option>
          <option value="Cursor">Cursor</option>
          <option value="Codex">Codex</option>
          <option value="Human">Human</option>
        </select>
      </label>
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
