"""Focused tests for layered, redacted MCP configuration checks."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def _write_config(path: Path, args: list[str]) -> None:
    path.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "filesystem": {
                        "command": "synthetic-command",
                        "args": args,
                    }
                }
            }
        ),
        encoding="utf-8",
    )


def test_one_server_config_is_valid_for_both_checkers(tmp_path: Path) -> None:
    config = tmp_path / "mcp.json"
    _write_config(config, ["-y", "synthetic-package", "."])

    commands = [
        [sys.executable, "scripts/check_mcp_config.py", "--config", str(config)],
        ["node", "scripts/check_mcp_config.js", "--config", str(config)],
    ]
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, completed.stderr
        assert "filesystem" in completed.stdout
        assert "not runtime claims" in completed.stdout


def test_checkers_do_not_echo_command_arguments(tmp_path: Path) -> None:
    marker = "SYNTHETIC_SECRET_ARGUMENT_9f3a"
    config = tmp_path / "mcp.json"
    _write_config(config, ["-y", marker, "."])

    commands = [
        [sys.executable, "scripts/check_mcp_config.py", "--config", str(config)],
        ["node", "scripts/check_mcp_config.js", "--config", str(config)],
    ]
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        combined = completed.stdout + completed.stderr
        assert marker not in combined


def test_checkers_redact_dangerous_path_value(tmp_path: Path) -> None:
    marker = "SYNTHETIC_SECRET_PATH_4a7c"
    config = tmp_path / "mcp.json"
    _write_config(config, ["-y", "synthetic-package", f"/Users/{marker}"])

    commands = [
        [sys.executable, "scripts/check_mcp_config.py", "--config", str(config)],
        ["node", "scripts/check_mcp_config.js", "--config", str(config)],
    ]
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        combined = completed.stdout + completed.stderr
        assert completed.returncode == 1
        assert "dangerous allowed path configured" in combined
        assert marker not in combined
