#!/usr/bin/env python3
"""Lightweight static check for .cursor/mcp.json (no secrets printed)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCP_PATH = ROOT / ".cursor" / "mcp.json"

DANGEROUS_PATH_PATTERNS = [
    re.compile(r"^/$"),
    re.compile(r"^[A-Za-z]:\\?$", re.I),
    re.compile(r"^~/?$"),
    re.compile(r"^/Users/[^/]+/?$"),
    re.compile(r"^/home/[^/]+/?$"),
    re.compile(r"^C:\\Users\\[^\\]+/?$", re.I),
]

SENSITIVE_ENV_KEYS = re.compile(
    r"(token|secret|password|api[_-]?key|cookie|session)",
    re.I,
)

SUPPORTED_SERVERS = {
    "chrome-devtools",
    "context7",
    "filesystem",
    "github",
    "playwright",
}


def _collect_path_args(server: dict) -> list[str]:
    args = server.get("args") or []
    if not isinstance(args, list):
        return []
    return [str(a) for a in args if isinstance(a, (str, int, float))]


def _is_dangerous_path(path_arg: str) -> bool:
    normalized = path_arg.strip().replace("\\", "/")
    for pat in DANGEROUS_PATH_PATTERNS:
        if pat.match(normalized):
            return True
    if normalized in ("/", "//", "C:", "C:/"):
        return True
    return False


def _has_literal_secret(value: str) -> bool:
    if not value or value.startswith("${"):
        return False
    if len(value) >= 20 and re.search(r"[a-zA-Z0-9]{20,}", value):
        if "env:" not in value and "GITHUB_TOKEN" not in value:
            return True
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only MCP configuration check")
    parser.add_argument("--config", type=Path, default=MCP_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mcp_path = args.config.resolve()
    print("MCP config: selected")
    if not mcp_path.exists():
        print("ERROR: .cursor/mcp.json not found")
        return 1

    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}")
        return 1

    servers = data.get("mcpServers") or {}
    if not isinstance(servers, dict):
        print("ERROR: mcpServers must be an object")
        return 1

    names = sorted(servers.keys())
    print(f"Servers ({len(names)}): {', '.join(names) or '(none)'}")

    errors: list[str] = []
    warnings: list[str] = []

    for name, cfg in servers.items():
        if not isinstance(cfg, dict):
            errors.append(f"{name}: config must be an object")
            continue

        if name == "filesystem" or "filesystem" in str(cfg.get("args", [])):
            for arg in _collect_path_args(cfg):
                if _is_dangerous_path(arg):
                    errors.append(
                        "filesystem: dangerous allowed path configured "
                        "(use project workspace only)"
                    )
                elif arg == ".":
                    warnings.append(
                        "filesystem: uses '.' — OK if Cursor cwd is repo root; "
                        "else set single-repo absolute path locally"
                    )

        env = cfg.get("env") or {}
        if isinstance(env, dict):
            for key, val in env.items():
                if SENSITIVE_ENV_KEYS.search(str(key)) and _has_literal_secret(
                    str(val)
                ):
                    errors.append(
                        f"{name}: env '{key}' looks like a hardcoded secret"
                    )
                if str(val).startswith("ghp_") or str(val).startswith("github_pat_"):
                    errors.append(f"{name}: GitHub token must not be committed")

    if "github" in names:
        gh = servers.get("github") or {}
        env = gh.get("env") if isinstance(gh, dict) else {}
        token_ref = ""
        if isinstance(env, dict):
            token_ref = str(env.get("GITHUB_PERSONAL_ACCESS_TOKEN", ""))
        if not token_ref.startswith("${env:"):
            warnings.append(
                "github: prefer ${env:GITHUB_TOKEN} in mcp.json; "
                "set GITHUB_TOKEN in shell/Cursor env (never commit token)"
            )

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        return 1
    print("OK: MCP config static check passed")
    print(
        "Supported candidates (not runtime claims): "
        + ", ".join(sorted(SUPPORTED_SERVERS))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
