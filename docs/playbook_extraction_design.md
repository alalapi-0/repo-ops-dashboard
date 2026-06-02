# Playbook / Skill Candidate Extraction

## Purpose

Turn **completed** `proof_of_work` records into **proposed** playbook/skill candidates. Nothing is promoted automatically; HumanOwner approves via `review_queue` (Round 51).

## Policy

- Live: `config/playbook_extraction_policy.yaml`
- Example: `governance/playbook_extraction_policy.example.yaml`
- Output registry: `governance/playbook_candidates.yaml`

## Commands

```bash
python3 scripts/extract_playbook_candidates.py
python3 scripts/extract_playbook_candidates.py --write
```

Default is **dry-run** with `auto_approve: true` for planning-only runs (no review_queue writes).

## Safety

- No external API; no managed-repo writes.
- Candidates stay `status: proposed` until HumanOwner acts.
