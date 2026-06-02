# Agent Gate Report

- generated_at: 2026-06-02T05:09:55.037149+00:00
- verdict: PASS

## Findings
- [PASS] `denylist`: denylist configured
- [PASS] `required_files`: required governance files exist
- [PASS] `env_tracked`: .env is not tracked
- [PASS] `secret_pattern`: no obvious secret patterns in tracked files
- [PASS] `dry_run_defaults`: dry-run defaults checked
- [PASS] `target_repo_modification`: no obvious target-repo write logic
- [PASS] `integration_docs_only`: integrations remain docs-only
- [PASS] `round_docs`: round docs 00-63 exist
- [PASS] `round_doc_sections`: round docs contain required sections
- [PASS] `ui_check_script`: ui_check.py exists
- [PASS] `audit_report`: round 25 architecture absorption audit report exists
- [PASS] `playwright_local`: ui_check uses local file:// access
- [PASS] `scan_allowlist`: scan script uses pattern-based allowlist collection
- [PASS] `protocol_governance_api`: governance round external API ban present in protocol
- [PASS] `protocol_version`: protocol v0.3.0 portfolio governance positioning present
- [PASS] `protocol_positioning`: Personal Agent OS positioning present
- [PASS] `governance_assets`: governance assets and design docs exist
- [PASS] `project_registry`: project_registry.yaml has 17 projects aligned with repos.yaml
- [PASS] `portfolio_state`: portfolio_state.yaml snapshot covers 17 projects
- [PASS] `governance_task_queue`: governance_task_queue.yaml lists 1 task(s)
- [PASS] `task_spec_template`: task_spec template contains required fields
- [PASS] `proof_of_work_template`: proof_of_work template contains required fields
- [PASS] `proof_of_work_registry`: proof_of_work_registry.yaml lists 1 record(s)
- [PASS] `agent_run_example`: example_run.jsonl valid with 5 event(s)
- [PASS] `review_queue`: review_queue.yaml valid with 5 open item(s)
- [PASS] `eval_registry`: eval registry contains required baseline evals
- [PASS] `completion_report`: round_31_completion_report.md exists
- [PASS] `requirements_dev`: requirements-dev.txt includes playwright and pytest
- [PASS] `installation_doc`: installation.md covers core refresh commands
- [PASS] `example_fixtures`: example data fixtures present
- [PASS] `pytest_tests`: pytest tests present (17 modules)
