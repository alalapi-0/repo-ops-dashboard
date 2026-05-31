#!/usr/bin/env python3
"""Real API generation pipeline with optional auto-approve review mode."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Run: pip install -r requirements.txt") from exc

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import generate_llm_summary as llm  # noqa: E402
import generation_review as review  # noqa: E402


def load_pipeline_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"generations": [], "updated_at": None}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_prompt_variants(status: dict[str, Any], daily_report: str, daily_brief: str, count: int) -> list[tuple[str, str]]:
    """Return (label, user_prompt) pairs up to count."""
    variants: list[tuple[str, str]] = [
        ("daily_summary", llm.build_user_prompt(status, daily_report, daily_brief)),
    ]
    repos = list(status.get("repos") or [])
    for repo in repos[: max(0, count - 1)]:
        name = repo.get("name", "unknown")
        blockers = "; ".join(repo.get("blockers") or []) or "无"
        prompt = (
            f"# 单仓聚焦\n\n仓库：{name}\n"
            f"priority={repo.get('priority', '?')}\nblockers={blockers}\n\n"
            "用简体中文输出 Markdown：## 今日行动（1条）、## 风险（1条）。"
            "不要编造未提供的仓库名；不要输出密钥或绝对路径。"
        )
        variants.append((f"repo_{name}", prompt))
    while len(variants) < count and repos:
        variants.append(variants[-1])
    return variants[:count]


def call_real_api(user_prompt: str) -> tuple[str, dict[str, Any]]:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY not set; refusing --call")

    base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    model = os.environ.get("LLM_MODEL", "deepseek/deepseek-v4-pro").strip()
    max_tokens = int(os.environ.get("LLM_MAX_TOKENS", "2048"))

    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": llm.SYSTEM_PROMPT},
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

    import urllib.error
    import urllib.request

    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw_text = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenRouter HTTP {exc.code}: {err_body[:500]}") from exc

    parsed = json.loads(raw_text)
    choices = parsed.get("choices") or []
    if not choices:
        raise SystemExit("OpenRouter returned no choices")
    content = str(choices[0].get("message", {}).get("content", "")).strip()
    if not content:
        raise SystemExit("OpenRouter returned empty content")

    generated_at = datetime.now(timezone.utc).isoformat()
    cleaned = (
        f"# LLM Generation\n\n"
        f"- generated_at: {generated_at}\n"
        f"- provider: openrouter\n"
        f"- model: {model}\n\n"
        f"{content}\n"
    )
    raw_record = {
        "generated_at": generated_at,
        "provider": "openrouter",
        "model": model,
        "request": {"model": model, "max_tokens": max_tokens, "user_prompt_chars": len(user_prompt)},
        "response": parsed,
    }
    return cleaned, raw_record


def process_generation(
    *,
    label: str,
    user_prompt: str,
    root: Path,
    settings: dict[str, Any],
    round_tag: str,
) -> dict[str, Any]:
    generation_id = f"{round_tag}_{label}_{uuid.uuid4().hex[:8]}"
    pending_dir = root / "pending" / generation_id
    approved_dir = root / "approved" / generation_id
    library_dir = root / "library" / generation_id
    pending_dir.mkdir(parents=True, exist_ok=True)

    cleaned, raw_record = call_real_api(user_prompt)
    quality = review.assess_quality(cleaned)
    provider = raw_record.get("provider", "openrouter")
    model = raw_record.get("model", os.environ.get("LLM_MODEL", "unknown"))

    (pending_dir / "content.md").write_text(cleaned, encoding="utf-8")
    (pending_dir / "raw.json").write_text(json.dumps(raw_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if review.should_auto_approve(settings):
        metadata = review.build_auto_approve_metadata(
            generation_id=generation_id,
            provider=str(provider),
            model=str(model),
            quality_status=quality,
            extra={"label": label, "round": round_tag},
        )
        target = approved_dir
        metadata["review_status"] = "auto_approved"
    else:
        metadata = review.build_pending_metadata(
            generation_id=generation_id,
            provider=str(provider),
            model=str(model),
            quality_status=quality,
        )
        target = pending_dir

    (pending_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if target != pending_dir:
        target.mkdir(parents=True, exist_ok=True)
        for name in ("content.md", "raw.json", "metadata.json"):
            shutil.copy2(pending_dir / name, target / name)
        if quality == "pass":
            library_dir.mkdir(parents=True, exist_ok=True)
            for name in ("content.md", "metadata.json"):
                shutil.copy2(target / name, library_dir / name)

    rel = str(target)
    return {
        "generation_id": generation_id,
        "label": label,
        "review_status": metadata["review_status"],
        "quality_status": quality,
        "approved_path": rel if target.exists() else None,
        "library_path": str(library_dir) if library_dir.exists() else None,
    }


def update_index(root: Path, entries: list[dict[str, Any]], round_tag: str) -> Path:
    index_path = root / "index.json"
    index = load_json(index_path)
    now = datetime.now(timezone.utc).isoformat()
    for entry in entries:
        index.setdefault("generations", []).append({**entry, "round": round_tag, "indexed_at": now})
    index["updated_at"] = now
    index["last_round"] = round_tag
    save_json(index_path, index)
    return index_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run real API generation pipeline with auto-approve mode")
    parser.add_argument("--config", default="config/generation_pipeline.yaml", help="Pipeline config YAML")
    parser.add_argument("--input", default="data/repo_status.example.json", help="Repo status JSON")
    parser.add_argument("--daily", default="reports/daily_repo_report.md", help="Daily report path")
    parser.add_argument("--brief", default="reports/daily_brief.md", help="Daily brief path")
    parser.add_argument("--count", type=int, default=0, help="Generation count (0=config default)")
    parser.add_argument("--round", default="round_1", help="Round tag for output paths")
    parser.add_argument("--call", action="store_true", help="Require real OpenRouter call")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve generations")
    parser.add_argument("--review-mode", choices=["auto", "manual"], default=None, help="Review mode override")
    parser.add_argument("--skip-human-review", action="store_true", help="Skip human review gate")
    parser.add_argument("--dry-run", action="store_true", help="Validate config only, no API calls")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.call and os.environ.get("LLM_ENABLED", "").strip().lower() != "true":
        raise SystemExit("LLM_ENABLED is not true; refusing --call")

    cfg = load_pipeline_config(Path(args.config))
    count = args.count or int(cfg.get("default_count", 3))
    count = min(count, int(cfg.get("max_count", 5)))
    root = Path(cfg.get("output_root", "data/generations"))

    settings = review.resolve_review_mode(
        cli_review_mode=args.review_mode,
        cli_auto_approve=True if args.auto_approve else None,
        cli_skip_human=True if args.skip_human_review else None,
    )
    if cfg.get("review_mode") == "auto" and args.review_mode is None and not args.auto_approve:
        settings = review.resolve_review_mode(cli_review_mode="auto", cli_auto_approve=True, cli_skip_human=True)

    print(f"[pipeline] review_mode={settings['review_mode']} auto_approve={settings['auto_approve']} count={count}")

    if args.dry_run:
        print("[pipeline] dry-run only; no API calls")
        return 0

    if not args.call:
        raise SystemExit("Refusing pipeline without --call (use dry-run to validate config)")

    status_path = Path(args.input)
    if not status_path.exists():
        raise SystemExit(f"Input not found: {status_path}")

    status = llm.load_json(status_path)
    daily_report = llm.load_text(Path(args.daily))
    daily_brief = llm.load_text(Path(args.brief), max_chars=4000)
    prompts = build_prompt_variants(status, daily_report, daily_brief, count)

    results: list[dict[str, Any]] = []
    failures = 0
    for label, user_prompt in prompts:
        try:
            entry = process_generation(
                label=label,
                user_prompt=user_prompt,
                root=root,
                settings=settings,
                round_tag=args.round,
            )
            results.append(entry)
            print(
                f"[ok] {entry['generation_id']} "
                f"status={entry['review_status']} quality={entry['quality_status']}"
            )
        except SystemExit as exc:
            failures += 1
            print(f"[fail] {label}: {exc}", file=sys.stderr)

    if results:
        index_path = update_index(root, results, args.round)
        print(f"[ok] index -> {index_path} ({len(results)} entries)")

        primary = root / "approved" / results[0]["generation_id"] / "content.md"
        if primary.exists():
            report_out = Path("reports/llm_daily_summary.md")
            report_out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(primary, report_out)
            print(f"[ok] promoted primary -> {report_out}")

    print(f"[pipeline] success={len(results)} failures={failures}")
    return 0 if results and failures == 0 else (1 if not results else 0)


if __name__ == "__main__":
    raise SystemExit(main())
