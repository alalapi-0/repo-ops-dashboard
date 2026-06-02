"""Tests for generate_cursor_prompt_from_task_spec."""

from __future__ import annotations

from pathlib import Path

import generate_cursor_prompt_from_task_spec as gen

ROOT = Path(__file__).resolve().parents[1]


def test_validate_example_task_spec() -> None:
    spec_path = ROOT / "governance" / "task_specs" / "example_task_spec.yaml"
    spec = gen.load_yaml(spec_path)
    assert gen.validate_task_spec(spec, spec_path.name) == []


def test_render_includes_task_id() -> None:
    spec = {
        "task_id": "task_demo_001",
        "project_id": "demo",
        "title": "Demo",
        "description": "Do something",
        "status": "proposed",
        "priority": "medium",
        "task_type": "prompt_generation",
        "working_directory": "/tmp/demo",
        "scope": ["read docs"],
        "out_of_scope": ["write secrets"],
        "reference_paths": ["README.md"],
        "acceptance_criteria": ["Prompt is safe"],
        "artifacts_expected": ["prompts/generated/demo.md"],
        "validation_commands": ["python3 scripts/agent_gate.py"],
        "blockers": [],
        "playbook_id": "demo.playbook",
        "confirmation_policy": "human_review",
        "execpolicy_profile": "readonly",
        "assigned_agent": "Cursor",
    }
    template = "# {{task_id}}\n{{acceptance_criteria}}\n"
    text = gen.render_task_spec(template, spec)
    assert "task_demo_001" in text
    assert "Prompt is safe" in text


def test_render_example_task_spec_template() -> None:
    spec_path = ROOT / "governance" / "task_specs" / "example_task_spec.yaml"
    template_path = ROOT / "prompts" / "cursor_from_task_spec.md"
    spec = gen.load_yaml(spec_path)
    template = gen.load_template(template_path)
    text = gen.render_task_spec(template, spec)
    assert "task_light_novel_governance_prompt_001" in text
    assert "light_novel" in text
    assert "acceptance_criteria" not in text
