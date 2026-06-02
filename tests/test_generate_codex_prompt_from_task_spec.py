"""Tests for generate_codex_prompt_from_task_spec."""

from __future__ import annotations

from pathlib import Path

import generate_codex_prompt_from_task_spec as gen

ROOT = Path(__file__).resolve().parents[1]


def test_validate_example_codex_task_spec() -> None:
    spec_path = ROOT / "governance" / "task_specs" / "example_codex_task_spec.yaml"
    spec = gen.load_yaml(spec_path)
    assert gen.validate_task_spec(spec, spec_path.name) == []


def test_render_codex_template() -> None:
    spec_path = ROOT / "governance" / "task_specs" / "example_codex_task_spec.yaml"
    template_path = ROOT / "prompts" / "codex_from_task_spec.md"
    spec = gen.load_yaml(spec_path)
    template = gen.load_template(template_path)
    text = gen.render_task_spec(template, spec)
    assert "task_repo_ops_test_fix_001" in text
    assert "Codex" not in text or "你是 Codex" in text
