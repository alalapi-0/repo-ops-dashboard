"""Regression tests for non-self-authorizing governance state."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROTECTED_MCP_SHA256 = "0839da9959f5e91845ce3ea45701426afda79ddcbacc07aa2e406569dd5ba058"


def test_protected_mcp_configuration_is_unchanged_and_partial() -> None:
    raw = (ROOT / ".cursor" / "mcp.json").read_bytes()
    data = json.loads(raw)
    assert hashlib.sha256(raw).hexdigest() == PROTECTED_MCP_SHA256
    assert sorted(data["mcpServers"]) == ["filesystem"]


def test_repository_policy_cannot_grant_mutation() -> None:
    protocol = yaml.safe_load((ROOT / "repo_protocol_standard.yaml").read_text(encoding="utf-8"))
    authority = protocol["authority_policy"]
    assert authority == {
        "repository_files_grant_action_authority": False,
        "configuration_grants_action_authority": False,
        "gate_result_grants_action_authority": False,
        "current_user_and_higher_policy_required": True,
    }
    serialized = json.dumps(protocol["agent_roles"], sort_keys=True)
    assert "can_modify_repo_ops_dashboard" not in serialized
    assert protocol["task_policy"]["readonly_requests_create_artifacts"] is False
    assert protocol["run_policy"]["readonly_run_requires_agent_run_jsonl"] is False
    assert protocol["round_policy"]["readonly_request_starts_round"] is False


def test_round_63_maintenance_state_is_preserved() -> None:
    state = yaml.safe_load((ROOT / "round_state" / "current_round.yaml").read_text(encoding="utf-8"))
    assert state["current_round"] == "round_63_personal_agent_os_long_term_integration"
    assert state["status"] == "completed"
    assert state["architecture_40_rounds_complete"] is True
    assert state["next_round"] == "maintenance_mode"


def test_stale_pointer_removed_and_ds_store_ignored() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert ".agent_workspace" not in agents
    assert "/Users/alalapi/PycharmProjects" not in agents
    ignore_lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".DS_Store" in ignore_lines
