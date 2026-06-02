#!/usr/bin/env python3
"""Generate static dashboard HTML from repository status data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


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
    parser.add_argument(
        "--portfolio-state",
        default="governance/portfolio_state.yaml",
        help="Portfolio state YAML for governance panel",
    )
    parser.add_argument(
        "--task-queue",
        default="governance/governance_task_queue.yaml",
        help="Governance task queue YAML",
    )
    parser.add_argument(
        "--review-queue",
        default="governance/review_queue.yaml",
        help="Review queue YAML",
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


def render_portfolio_panel(data: dict[str, Any]) -> str:
    if not data:
        return ""
    summary = dict(data.get("summary", {}))
    projects = list(data.get("projects", []))
    blocked = [p for p in projects if p.get("blockers")]
    rows = "".join(
        f"<tr><td>{esc(p.get('project_id', ''))}</td>"
        f"<td>{esc(p.get('lifecycle', ''))}</td>"
        f"<td>{esc(p.get('priority', ''))}</td>"
        f"<td>{esc(len(p.get('blockers') or []))}</td></tr>"
        for p in projects[:8]
    )
    return f"""
    <article class="gov-panel" data-panel="portfolio_state">
      <h3>Portfolio State</h3>
      <p class="gov-meta">生成：{esc(data.get("generated_at", "—"))}</p>
      <div class="gov-stats">
        <span>项目 {esc(summary.get("total_projects", 0))}</span>
        <span>活跃 {esc(summary.get("active_projects", 0))}</span>
        <span>卡住 {esc(summary.get("blocked_projects", 0))}</span>
        <span>Review 开放 {esc(summary.get("review_queue_open", 0))}</span>
      </div>
      <table class="gov-table">
        <thead><tr><th>project_id</th><th>lifecycle</th><th>priority</th><th>blockers</th></tr></thead>
        <tbody>{rows or '<tr><td colspan="4">无项目</td></tr>'}</tbody>
      </table>
      <p class="gov-foot">展示 {min(len(projects), 8)}/{len(projects)} 项目 · 有卡点 {len(blocked)}</p>
    </article>
    """


def render_task_queue_panel(data: dict[str, Any]) -> str:
    if not data:
        return ""
    summary = dict(data.get("summary", {}))
    tasks = list(data.get("tasks", []))
    rows = "".join(
        f"<tr><td>{esc(t.get('task_id', ''))}</td>"
        f"<td>{esc(t.get('project_id', ''))}</td>"
        f"<td>{esc(t.get('status', ''))}</td>"
        f"<td>{esc(t.get('assigned_agent', ''))}</td></tr>"
        for t in tasks[:6]
    )
    return f"""
    <article class="gov-panel" data-panel="task_queue">
      <h3>Task Queue</h3>
      <p class="gov-meta">生成：{esc(data.get("generated_at", "—"))}</p>
      <div class="gov-stats">
        <span>总任务 {esc(summary.get("total_tasks", 0))}</span>
        <span>活跃 {esc(summary.get("active_tasks", 0))}</span>
      </div>
      <table class="gov-table">
        <thead><tr><th>task_id</th><th>project</th><th>status</th><th>agent</th></tr></thead>
        <tbody>{rows or '<tr><td colspan="4">无任务</td></tr>'}</tbody>
      </table>
    </article>
    """


def render_review_queue_panel(data: dict[str, Any]) -> str:
    if not data:
        return ""
    items = [item for item in data.get("items", []) if str(item.get("status", "")).lower() == "open"]
    rows = "".join(
        f"<tr><td>{esc(item.get('review_id', ''))}</td>"
        f"<td>{esc(item.get('type', ''))}</td>"
        f"<td>{esc(item.get('project_id', ''))}</td></tr>"
        for item in items[:6]
    )
    return f"""
    <article class="gov-panel" data-panel="review_queue">
      <h3>Review Queue</h3>
      <p class="gov-meta">更新：{esc(data.get("updated_at", "—"))}</p>
      <div class="gov-stats">
        <span>开放 {len(items)}</span>
      </div>
      <table class="gov-table">
        <thead><tr><th>review_id</th><th>type</th><th>project</th></tr></thead>
        <tbody>{rows or '<tr><td colspan="3">无开放项</td></tr>'}</tbody>
      </table>
    </article>
    """


def render_blockers_panel(repos: list[dict[str, Any]]) -> str:
    rows: list[str] = []
    for repo in repos:
        blockers = list(repo.get("blockers") or [])
        if not blockers:
            continue
        details = list(repo.get("blocker_details") or [])
        escalation = str(repo.get("blocker_max_escalation", "info"))
        if details:
            types = ", ".join(str(d.get("type", "")) for d in details)
            owners = ", ".join(sorted({str(d.get("owner", "")) for d in details}))
            detail_text = f"{esc(types)} · 升级 {esc(escalation)} · 负责 {esc(owners)}"
        else:
            detail_text = esc("; ".join(blockers))
        rows.append(
            f"<tr><td>{esc(repo.get('name', ''))}</td>"
            f"<td>{esc('; '.join(blockers))}</td>"
            f"<td>{detail_text}</td></tr>"
        )
    body = "".join(rows) or '<tr><td colspan="3">无卡点</td></tr>'
    return f"""
    <article class="gov-panel" data-panel="blockers">
      <h3>Blockers</h3>
      <div class="gov-stats">
        <span>卡住仓库 {len(rows)}</span>
      </div>
      <table class="gov-table">
        <thead><tr><th>仓库</th><th>卡点</th><th>分类/升级</th></tr></thead>
        <tbody>{body}</tbody>
      </table>
    </article>
    """


def render_governance_v2(
    portfolio: dict[str, Any],
    task_queue: dict[str, Any],
    review_queue: dict[str, Any],
    repos: list[dict[str, Any]],
) -> str:
    panels = (
        render_portfolio_panel(portfolio)
        + render_task_queue_panel(task_queue)
        + render_review_queue_panel(review_queue)
        + render_blockers_panel(repos)
    )
    if not panels.strip():
        return ""
    return f"""
    <section class="governance-v2" data-dashboard-v2-ready="true">
      <h2>治理面板 V2</h2>
      <div class="gov-panels">{panels}</div>
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

    portfolio_path = Path(args.portfolio_state)
    task_queue_path = Path(args.task_queue)
    review_queue_path = Path(args.review_queue)
    portfolio_data = load_yaml(portfolio_path)
    task_queue_data = load_yaml(task_queue_path)
    review_queue_data = load_yaml(review_queue_path)

    payload = load_json(input_path)
    repos = list(payload.get("repos", []))
    governance_v2_html = render_governance_v2(portfolio_data, task_queue_data, review_queue_data, repos)
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
    {governance_v2_html}
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
