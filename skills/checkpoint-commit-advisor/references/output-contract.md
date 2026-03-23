# Output Contract

## Required Fields
- `decision`
- `decision_reason`
- `strategy`
- `dirty_tree_summary`
- `health_flags`
- `buckets`
- `messages`
- `confirmation_points`
- `risks`
- `suggested_commands`

## Decision Enum
- `commit_now`
- `defer`

## Strategy Enum
- `single-snapshot`
- `two-layer`
- `three-layer`
- `null` when the decision is `defer`

## Bucket Kinds
- `governance_anchor`
- `implementation_snapshot`
- `supporting_docs_snapshot`
- `mixed_snapshot`

## Message Semantics
- Governance anchor messages should use honest governance wording such as `chore(plan): ...`.
- Known-bad snapshots should use explicit checkpoint wording such as `checkpoint(wip): ...`.
- Supporting-doc buckets should not be mislabeled as fixes or refactors.

## CLI Quality Bar
- `analyze --json` must emit a stable JSON object.
- The script must not mutate git history or working files.
- Blocking health issues must be surfaced in `health_flags` and influence `decision`.
