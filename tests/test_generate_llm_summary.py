"""Tests for generate_llm_summary."""

from __future__ import annotations

import json
import sys
from io import BytesIO
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import generate_llm_summary as llm  # noqa: E402


def test_placeholder_markdown_contains_dry_run() -> None:
    text = llm.placeholder_markdown()
    assert "dry-run" in text


def test_build_user_prompt_includes_repo_names() -> None:
    status = {"repos": [{"name": "demo-repo", "priority": "high", "blockers": []}]}
    prompt = llm.build_user_prompt(status, "daily text", "brief text")
    assert "demo-repo" in prompt
    assert "brief text" in prompt


def test_call_openrouter_success() -> None:
    payload = {
        "choices": [{"message": {"content": "## 今日三条行动\n- 推进 demo"}}],
    }
    body = json.dumps(payload).encode("utf-8")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return body

    with mock.patch.dict(
        "os.environ",
        {
            "OPENROUTER_API_KEY": "test-key",
            "LLM_MODEL": "anthropic/claude-sonnet-4",
        },
        clear=False,
    ):
        with mock.patch("urllib.request.urlopen", return_value=FakeResponse()):
            text = llm.call_openrouter("hello")
    assert "今日三条行动" in text
    assert "test-key" not in text


def test_call_refuses_without_api_key() -> None:
    with mock.patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}, clear=False):
        try:
            llm.call_openrouter("hello")
            raised = False
        except SystemExit as exc:
            raised = "OPENROUTER_API_KEY" in str(exc)
        assert raised


def test_main_dry_run_writes_file(tmp_path: Path) -> None:
    status_path = tmp_path / "status.json"
    status_path.write_text('{"repos": [{"name": "a", "priority": "low", "blockers": []}]}', encoding="utf-8")
    out = tmp_path / "llm.md"
    argv = [
        "generate_llm_summary.py",
        "--input",
        str(status_path),
        "--daily",
        str(tmp_path / "missing.md"),
        "--brief",
        str(tmp_path / "missing_brief.md"),
        "--output",
        str(out),
    ]
    with mock.patch.object(sys, "argv", argv):
        assert llm.main() == 0
    assert "dry-run" in out.read_text(encoding="utf-8")
