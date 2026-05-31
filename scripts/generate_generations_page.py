#!/usr/bin/env python3
"""Static HTML page listing LLM generations from data/generations/index.json."""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_index(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"generations": [], "updated_at": None}
    return json.loads(path.read_text(encoding="utf-8"))


def render_page(index: dict[str, Any]) -> str:
    rows: list[str] = []
    for item in reversed(index.get("generations") or []):
        gid = html.escape(str(item.get("generation_id", "")))
        status = html.escape(str(item.get("review_status", "unknown")))
        quality = html.escape(str(item.get("quality_status", "")))
        label = html.escape(str(item.get("label", "")))
        approved = html.escape(str(item.get("approved_path") or ""))
        badge = "auto" if status == "auto_approved" else status
        rows.append(
            f"<tr><td>{gid}</td><td>{label}</td>"
            f'<td><span class="badge {badge}">{status}</span></td>'
            f"<td>{quality}</td><td><code>{approved}</code></td></tr>"
        )
    body_rows = "\n".join(rows) if rows else '<tr><td colspan="5">暂无生成记录</td></tr>'
    updated = html.escape(str(index.get("updated_at") or "—"))
    generated_at = datetime.now(timezone.utc).isoformat()
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Generations Review</title>
  <link rel="stylesheet" href="style.css" />
  <style>
    table {{ width: 100%; border-collapse: collapse; margin-top: 16px; background: white; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: left; font-size: 14px; }}
    th {{ background: #f9fafb; }}
    .badge.auto {{ background: #d1fae5; color: #065f46; padding: 2px 8px; border-radius: 6px; }}
    .badge.pending {{ background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 6px; }}
    code {{ font-size: 12px; word-break: break-all; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>LLM Generations</h1>
    <p>真实 API 生成结果与审核状态（auto 模式下自动通过，不阻塞流程）</p>
    <p><small>index 更新：{updated} · 页面生成：{generated_at}</small></p>
    <p><a href="hub.html">← Hub</a> · <a href="index.html">Dashboard</a></p>
    <table>
      <thead>
        <tr><th>ID</th><th>Label</th><th>Review</th><th>Quality</th><th>Path</th></tr>
      </thead>
      <tbody>
        {body_rows}
      </tbody>
    </table>
  </div>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate generations review HTML")
    parser.add_argument("--index", default="data/generations/index.json", help="Generations index JSON")
    parser.add_argument("--output", default="dashboard/generations.html", help="Output HTML path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    index = load_index(Path(args.index))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_page(index), encoding="utf-8")
    print(f"[ok] generations page -> {output} ({len(index.get('generations') or [])} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
