#!/usr/bin/env python3
"""Parse and validate governance/execpolicy/*.rules document-level constraints."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RULE_LINE = re.compile(r"^(allow|deny|prompt)\s+(read|write|command)\s+(.+)$")

REQUIRED_PORTFOLIO_CHECKS: tuple[tuple[str, str, str], ...] = (
    ("deny", "read", "**/.env"),
    ("deny", "read", "**/.env.*"),
    ("deny", "read", "**/*secret*"),
    ("deny", "read", "**/*token*"),
    ("deny", "write", "managed_repos/**"),
    ("prompt", "write", "**"),
)

REQUIRED_PORTFOLIO_COMMAND_PROMPTS = ("rm -rf", "launchctl")

KNOWN_PROFILES = (
    "readonly_managed_repo",
    "repo_ops_guarded",
    "risky_confirm",
)


@dataclass(frozen=True)
class ExecRule:
    action: str
    kind: str
    pattern: str
    source: str
    line_no: int


def parse_rules_text(text: str, source: str = "") -> tuple[list[ExecRule], list[str]]:
    rules: list[ExecRule] = []
    errors: list[str] = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = RULE_LINE.match(line)
        if not match:
            errors.append(f"{source}:{line_no}: invalid rule syntax: {raw.strip()}")
            continue
        action, kind, pattern = match.groups()
        rules.append(
            ExecRule(
                action=action,
                kind=kind,
                pattern=pattern.strip(),
                source=source,
                line_no=line_no,
            )
        )
    return rules, errors


def read_execpolicy_file(path: Path) -> tuple[list[ExecRule], list[str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    return parse_rules_text(text, source=path.name)


def rule_key(rule: ExecRule) -> tuple[str, str, str]:
    return (rule.action, rule.kind, rule.pattern)


def validate_required_rules(rules: list[ExecRule], required: tuple[tuple[str, str, str], ...]) -> list[str]:
    present = {rule_key(rule) for rule in rules}
    missing = [f"{action} {kind} {pattern}" for action, kind, pattern in required if (action, kind, pattern) not in present]
    errors = [f"missing required rule: {item}" for item in missing]
    command_rules = [rule for rule in rules if rule.kind == "command" and rule.action == "prompt"]
    if not any("push" in rule.pattern for rule in command_rules):
        push_label = "git" + " push"
        errors.append(f"missing required rule: prompt command {push_label}")
    for token in REQUIRED_PORTFOLIO_COMMAND_PROMPTS:
        if not any(token in rule.pattern for rule in command_rules):
            errors.append(f"missing required rule: prompt command {token}")
    return errors


def validate_execpolicy_file(path: Path, *, required: tuple[tuple[str, str, str], ...] | None = None) -> list[str]:
    rules, errors = read_execpolicy_file(path)
    if required:
        errors.extend(validate_required_rules(rules, required))
    return errors


def validate_execpolicy_dir(root: Path) -> list[str]:
    errors: list[str] = []
    portfolio = root / "portfolio.rules"
    if not portfolio.exists():
        return ["portfolio.rules missing"]
    errors.extend(validate_execpolicy_file(portfolio, required=REQUIRED_PORTFOLIO_CHECKS))

    profiles_dir = root / "profiles"
    if not profiles_dir.is_dir():
        errors.append("profiles/ directory missing")
        return errors

    for profile_name in KNOWN_PROFILES:
        profile_path = profiles_dir / f"{profile_name}.rules"
        if not profile_path.exists():
            errors.append(f"missing profile: {profile_name}.rules")
            continue
        errors.extend(validate_execpolicy_file(profile_path))

    for profile_path in sorted(profiles_dir.glob("*.rules")):
        _, parse_errors = read_execpolicy_file(profile_path)
        errors.extend(parse_errors)

    return errors


def summarize_execpolicy(rules: list[ExecRule]) -> dict[str, Any]:
    counts = {"allow": 0, "deny": 0, "prompt": 0}
    for rule in rules:
        counts[rule.action] = counts.get(rule.action, 0) + 1
    return {
        "total_rules": len(rules),
        **counts,
        "read_rules": sum(1 for rule in rules if rule.kind == "read"),
        "write_rules": sum(1 for rule in rules if rule.kind == "write"),
        "command_rules": sum(1 for rule in rules if rule.kind == "command"),
    }


def _glob_match(pattern: str, value: str) -> bool:
    regex = "^" + re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*") + "$"
    return re.match(regex, value) is not None


def classify_path(rules: list[ExecRule], action: str, path: str) -> str:
    action = action.lower()
    matched: ExecRule | None = None
    for rule in rules:
        if rule.kind != action:
            continue
        if _glob_match(rule.pattern, path):
            matched = rule
    if matched is None:
        return "unknown"
    return matched.action


def classify_command(rules: list[ExecRule], command: str) -> str:
    command = command.strip()
    matched: ExecRule | None = None
    for rule in rules:
        if rule.kind != "command":
            continue
        if _glob_match(rule.pattern, command):
            matched = rule
    if matched is None:
        return "unknown"
    return matched.action


def load_profile_rules(root: Path, profile: str) -> list[ExecRule]:
    portfolio_rules, _ = read_execpolicy_file(root / "portfolio.rules")
    profile_path = root / "profiles" / f"{profile}.rules"
    profile_rules, errors = read_execpolicy_file(profile_path)
    if errors:
        raise ValueError("; ".join(errors))
    return portfolio_rules + profile_rules
