#!/usr/bin/env python3
"""Generate LLM daily summary via OpenRouter (dry-run default; --call opt-in)."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SYSTEM_PROMPT = (
    "你是个人多仓库治理助手。根据仓库状态与日报，用简体中文输出 Markdown，"
    "包含：## 今日三条行动、## 一条暂缓、## 风险提醒。"
    "每条行动不超过 80 字；不要编造未提供的仓库名；不要输出密钥或本地绝对路径。"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path, *, max_chars: int = 8000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if len(text) > max_chars:
        return text[: max_chars - 20] + "\n\n…（已截断）\n"
    return text


def summarize_repos(status: dict[str, Any], *, limit: int = 12) -> str:
    lines: list[str] = []
    for repo in list(status.get("repos", []))[:limit]:
        name = repo.get("name", "unknown")
        priority = repo.get("priority", "?")
        blockers = "; ".join(repo.get("blockers") or []) or "无"
        lines.append(f"- {name} | priority={priority} | blockers={blockers}")
    return "\n".join(lines) or "- 无仓库数据"


def build_user_prompt(
    status: dict[str, Any],
    daily_report: str,
    daily_brief: str,
) -> str:
    return (
        "# 输入数据\n\n"
        "## 仓库摘要\n"
        f"{summarize_repos(status)}\n\n"
        "## 规则每日简报\n"
        f"{daily_brief or '（无）'}\n\n"
        "## 日报摘录\n"
        f"{daily_report or '（无）'}\n"
    )


def placeholder_markdown() -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    return (
        f"# LLM Daily Summary\n\n"
        f"- generated_at: {generated_at}\n"
        f"- mode: dry-run（未调用 OpenRouter）\n\n"
        "## 今日三条行动\n\n"
        "- （启用 LLM：设置 LLM_ENABLED=true 并运行 --call）\n\n"
        "## 一条暂缓\n\n"
        "- 见规则 daily_brief\n\n"
        "## 风险提醒\n\n"
        "- 无 LLM 输出\n"
    )


def call_openrouter(user_prompt: str) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY not set; refusing --call")

    base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    model = os.environ.get("LLM_MODEL", "anthropic/claude-sonnet-4").strip()
    max_tokens = int(os.environ.get("LLM_MAX_TOKENS", "2048"))

    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    referer = os.environ.get("OPENROUTER_HTTP_REFERER", "").strip()
    title = os.environ.get("OPENROUTER_X_TITLE", "").strip()
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title

    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenRouter HTTP {exc.code}: {err_body[:500]}") from exc

    parsed = json.loads(raw)
    choices = parsed.get("choices") or []
    if not choices:
        raise SystemExit("OpenRouter returned no choices")
    content = choices[0].get("message", {}).get("content", "")
    if not str(content).strip():
        raise SystemExit("OpenRouter returned empty content")
    generated_at = datetime.now(timezone.utc).isoformat()
    return f"# LLM Daily Summary\n\n- generated_at: {generated_at}\n- provider: openrouter\n\n{content.strip()}\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate LLM daily summary (OpenRouter opt-in)")
    parser.add_argument("--input", default="data/repo_status.json", help="Repo status JSON")
    parser.add_argument("--daily", default="reports/daily_repo_report.md", help="Daily report path")
    parser.add_argument("--brief", default="reports/daily_brief.md", help="Rule-based daily brief")
    parser.add_argument("--output", default="reports/llm_daily_summary.md", help="Output markdown")
    parser.add_argument(
        "--call",
        action="store_true",
        help="Opt-in OpenRouter call (requires OPENROUTER_API_KEY, LLM_ENABLED=true)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status_path = Path(args.input)
    if not status_path.exists():
        raise SystemExit(f"Input not found: {status_path}")

    if args.call and os.environ.get("LLM_ENABLED", "").strip().lower() != "true":
        raise SystemExit("LLM_ENABLED is not true; refusing --call")

    status = load_json(status_path)
    daily_report = load_text(Path(args.daily))
    daily_brief = load_text(Path(args.brief), max_chars=4000)

    if args.call:
        user_prompt = build_user_prompt(status, daily_report, daily_brief)
        content = call_openrouter(user_prompt)
    else:
        content = placeholder_markdown()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    mode = "call" if args.call else "dry-run"
    print(f"[ok] llm summary ({mode}) -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
