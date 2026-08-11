"""Tests for execpolicy rule parsing and classification."""

from __future__ import annotations

from pathlib import Path

import validate_execpolicy as vep


def test_portfolio_rules_validate() -> None:
    root = Path(__file__).resolve().parents[1]
    errors = vep.validate_execpolicy_dir(root / "governance" / "execpolicy")
    assert not errors


def test_parse_invalid_line_reports_error() -> None:
    _, errors = vep.parse_rules_text("bad line\nallow read README.md", source="test.rules")
    assert any("invalid rule syntax" in err for err in errors)


def test_classify_deny_env_read() -> None:
    root = Path(__file__).resolve().parents[1]
    rules, _ = vep.read_execpolicy_file(root / "governance" / "execpolicy" / "portfolio.rules")
    assert vep.classify_path(rules, "read", "/tmp/project/.env") == "deny"


def test_classify_prompt_git_push() -> None:
    root = Path(__file__).resolve().parents[1]
    rules = vep.load_profile_rules(root / "governance" / "execpolicy", "risky_confirm")
    assert vep.classify_command(rules, "git" + " push") == "prompt"


def test_summarize_counts_actions() -> None:
    root = Path(__file__).resolve().parents[1]
    rules, _ = vep.read_execpolicy_file(root / "governance" / "execpolicy" / "portfolio.rules")
    summary = vep.summarize_execpolicy(rules)
    assert summary["total_rules"] >= 8
    assert summary["deny"] >= 4


def test_no_active_execpolicy_grants_write() -> None:
    root = Path(__file__).resolve().parents[1]
    execpolicy = root / "governance" / "execpolicy"
    for path in [execpolicy / "portfolio.rules", *sorted((execpolicy / "profiles").glob("*.rules"))]:
        rules, errors = vep.read_execpolicy_file(path)
        assert not errors
        assert not any(rule.action == "allow" and rule.kind == "write" for rule in rules)
