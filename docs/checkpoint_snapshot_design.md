# Checkpoint Snapshot Design

## Purpose

Persist periodic **portfolio_state** snapshots under `governance/checkpoints/` for audit, rollback comparison, and failure-recovery `checkpoint_id` binding (see `docs/failure_recovery_design.md`).

## Policy

Live config: `config/checkpoint_snapshot_policy.yaml`  
Example mirror: `governance/checkpoint_snapshot_policy.example.yaml`

| Field | Meaning |
|-------|---------|
| `snapshot.source` | Input `governance/portfolio_state.yaml` |
| `snapshot.output_dir` | Directory for checkpoint YAML files |
| `snapshot.manifest` | Index of retained checkpoints |
| `snapshot.id_prefix` | Checkpoint id prefix (e.g. `ckpt_portfolio_`) |
| `snapshot.max_retained` | Prune manifest to this many newest entries |
| `defaults.dry_run` | Default: plan only, no file writes |

## Commands

```bash
python3 scripts/sync_portfolio_state.py
python3 scripts/validate_checkpoint_snapshot_policy.py
python3 scripts/snapshot_portfolio_checkpoint.py          # dry-run
python3 scripts/snapshot_portfolio_checkpoint.py --write
```

`refresh_status.sh --example` runs sync + dry-run snapshot after portfolio sync.

## Safety

- Read-only on managed repos; writes only under this governance repo.
- No `.env`, secrets, or external API.
- HumanOwner approves destructive lifecycle changes separately via `review_queue`.
