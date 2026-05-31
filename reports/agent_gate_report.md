# Agent Gate Report

- generated_at: 2026-05-31T05:42:46.937237+00:00
- verdict: WARNING

## Findings
- [PASS] `denylist`: denylist configured
- [PASS] `required_files`: required governance files exist
- [PASS] `env_tracked`: .env is not tracked
- [PASS] `secret_pattern`: no obvious secret patterns in tracked files
- [PASS] `dry_run_defaults`: dry-run defaults checked
- [WARNING] `target_repo_modification`: review risky tokens: ['agent_gate.py:git commit', 'agent_gate.py:git push', 'agent_gate.py:shutil.rmtree', 'agent_gate.py:os.remove(', 'agent_gate.py:Path.unlink(']
- [WARNING] `integration_docs_only`: integration keyword found: ['agent_gate.py:feishu', 'agent_gate.py:lark_oapi', 'agent_gate.py:telegram', 'agent_gate.py:openclaw_sdk']
