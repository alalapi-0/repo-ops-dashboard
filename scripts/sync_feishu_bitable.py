#!/usr/bin/env python3
"""Sync repo_status.json rows to Feishu Bitable (dry-run by default; --sync opt-in)."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FEISHU_API = "https://open.feishu.cn/open-apis"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def api_request(
    method: str,
    url: str,
    *,
    token: str | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {raw[:500]}") from exc
    parsed = json.loads(raw)
    if parsed.get("code", 0) != 0:
        raise RuntimeError(f"Feishu API code={parsed.get('code')} msg={parsed.get('msg', '')}")
    return parsed


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    url = f"{FEISHU_API}/auth/v3/tenant_access_token/internal"
    parsed = api_request("POST", url, body={"app_id": app_id, "app_secret": app_secret})
    token = parsed.get("tenant_access_token")
    if not token:
        raise RuntimeError("tenant_access_token missing in response")
    return str(token)


def parse_iso_to_ms(value: str | None) -> int | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp() * 1000)
    except ValueError:
        return None


def join_list(items: list[Any] | None) -> str:
    if not items:
        return ""
    return "; ".join(str(item) for item in items)


def repo_to_fields(repo: dict[str, Any], sync_at_ms: int) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "repo_name": repo.get("name", ""),
        "type": repo.get("type", ""),
        "priority": repo.get("priority", ""),
        "health_score": repo.get("health_score", 0),
        "lifecycle_status": repo.get("lifecycle_status", repo.get("status", "")),
        "blockers": join_list(repo.get("blockers")),
        "recommended_agent": repo.get("recommended_agent", ""),
        "next_actions": join_list(repo.get("next_actions")),
        "sync_at": sync_at_ms,
    }
    last_checked_ms = parse_iso_to_ms(repo.get("last_checked"))
    if last_checked_ms is not None:
        fields["last_checked"] = last_checked_ms
    return fields


def list_all_records(token: str, app_token: str, table_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    page_token: str | None = None
    while True:
        query = f"page_size=500"
        if page_token:
            query += f"&page_token={page_token}"
        url = f"{FEISHU_API}/bitable/v1/apps/{app_token}/tables/{table_id}/records?{query}"
        parsed = api_request("GET", url, token=token)
        data = parsed.get("data") or {}
        items = data.get("items") or []
        records.extend(items)
        if not data.get("has_more"):
            break
        page_token = data.get("page_token")
        if not page_token:
            break
    return records


def build_repo_name_index(records: list[dict[str, Any]]) -> dict[str, str]:
    index: dict[str, str] = {}
    for record in records:
        record_id = record.get("record_id")
        fields = record.get("fields") or {}
        name = fields.get("repo_name")
        if isinstance(name, list) and name:
            name = name[0].get("text") if isinstance(name[0], dict) else name[0]
        if isinstance(name, str) and record_id:
            index[name] = str(record_id)
    return index


def create_record(
    token: str, app_token: str, table_id: str, fields: dict[str, Any]
) -> None:
    url = f"{FEISHU_API}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    api_request("POST", url, token=token, body={"fields": fields})


def update_record(
    token: str, app_token: str, table_id: str, record_id: str, fields: dict[str, Any]
) -> None:
    url = f"{FEISHU_API}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
    api_request("PUT", url, token=token, body={"fields": fields})


def load_credentials() -> tuple[str, str, str, str]:
    app_id = os.environ.get("FEISHU_APP_ID", "").strip()
    app_secret = os.environ.get("FEISHU_APP_SECRET", "").strip()
    app_token = os.environ.get("FEISHU_BITABLE_APP_TOKEN", "").strip()
    table_id = os.environ.get("FEISHU_BITABLE_TABLE_ID", "").strip()
    missing = [
        name
        for name, value in [
            ("FEISHU_APP_ID", app_id),
            ("FEISHU_APP_SECRET", app_secret),
            ("FEISHU_BITABLE_APP_TOKEN", app_token),
            ("FEISHU_BITABLE_TABLE_ID", table_id),
        ]
        if not value
    ]
    if missing:
        raise SystemExit(f"Missing env for --sync: {', '.join(missing)}")
    return app_id, app_secret, app_token, table_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync repo_status.json to Feishu Bitable")
    parser.add_argument("--input", default="data/repo_status.json", help="Input repo_status.json")
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Write to Feishu (requires FEISHU_APP_* and FEISHU_BITABLE_* env)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    status_data = load_json(input_path)
    repos = status_data.get("repos") or []
    sync_at_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    planned: list[tuple[str, str, dict[str, Any]]] = []
    for repo in repos:
        name = repo.get("name", "")
        if not name:
            continue
        fields = repo_to_fields(repo, sync_at_ms)
        planned.append((name, "upsert", fields))

    print(f"[bitable] repos={len(planned)} mode={'sync' if args.sync else 'dry-run'}")
    for name, action, fields in planned:
        summary = (
            f"  {name}: priority={fields.get('priority')} "
            f"health={fields.get('health_score')} "
            f"blockers={len(fields.get('blockers', '').split('; ')) if fields.get('blockers') else 0}"
        )
        print(summary)

    if not args.sync:
        print("[bitable] dry-run complete (no API calls). Use --sync to write.")
        return 0

    app_id, app_secret, app_token, table_id = load_credentials()
    token = get_tenant_access_token(app_id, app_secret)
    existing = list_all_records(token, app_token, table_id)
    name_index = build_repo_name_index(existing)

    created = 0
    updated = 0
    for name, _, fields in planned:
        if name in name_index:
            update_record(token, app_token, table_id, name_index[name], fields)
            updated += 1
        else:
            create_record(token, app_token, table_id, fields)
            created += 1

    print(f"[ok] bitable sync: created={created} updated={updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
