# Agent Gate Report

- generated_at: 2026-05-31T08:38:59.708983+00:00
- verdict: PASS

## Findings
- [PASS] `denylist`: denylist configured
- [PASS] `required_files`: required governance files exist
- [PASS] `env_tracked`: .env is not tracked
- [PASS] `secret_pattern`: no obvious secret patterns in tracked files
- [PASS] `dry_run_defaults`: dry-run defaults checked
- [PASS] `target_repo_modification`: no obvious target-repo write logic
- [PASS] `integration_docs_only`: integrations remain docs-only
- [PASS] `round_docs`: round docs 00-15 exist
- [PASS] `round_doc_sections`: round docs contain required sections
- [PASS] `ui_check_script`: ui_check.py exists
- [PASS] `audit_report`: round 01 audit report exists
- [PASS] `playwright_local`: ui_check uses local file:// access
- [PASS] `scan_allowlist`: scan script uses pattern-based allowlist collection
- [PASS] `protocol_round1_api`: Round 1 external API ban present in protocol
- [PASS] `requirements_dev`: requirements-dev.txt includes playwright
