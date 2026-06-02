# Project Rule Promotion

## Purpose

Turn **playbook_candidates** into **review_queue** proposals for promoting repeatable rules into per-project `.cursor/rules` or `AGENTS.md` guidance. Agents never auto-approve; HumanOwner merges and closes items.

## Policy

- Live: `config/project_rule_promotion_policy.yaml`
- Proposal queue: `governance/project_rule_promotion_queue.yaml`
- Canonical HITL queue: `governance/review_queue.yaml` (merge only with explicit flags)

## Commands

```bash
python3 scripts/promote_project_rule.py
python3 scripts/promote_project_rule.py --write
# Optional explicit merge (off by default):
python3 scripts/promote_project_rule.py --write --merge-review-queue
```

Default: **dry-run** + `merge_into_review_queue: false`.

## Safety

- No automatic writes to `review_queue.yaml` unless `--merge-review-queue`.
- No managed-repo or secret access.
