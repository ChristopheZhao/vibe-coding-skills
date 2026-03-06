# Schemas

## L1: Project State (`docs/memory/state/current.json`)

Required fields:
- `version`: integer
- `updated_at`: UTC timestamp
- `plan_id`: string or null
- `topic_id`: string or null
- `stage`: string or null
- `goal`: string or null
- `blockers`: array of strings
- `next_action`: string or null
- `last_event_id`: string or null
- `anchors`: object (`branch`, `head_sha`, `files_fingerprint`)

## L2: Event Record (`docs/memory/events/events.jsonl`)

Required fields per line:
- `id`
- `timestamp`
- `event_type` (`decision|experiment|blocker|fix|rollback|milestone|note`)
- `summary`
- `impact` (`low|medium|high`)
- `result` (`unknown|success|failed|mixed`)
- `is_key_event`
- `key_score`
- `anchors`

Recommended fields:
- `plan_id`
- `topic_id`
- `milestone_id`
- `problem_key`
- `next_action`
- `doc_refs` (pointer-first references to docs/ADR/runbook sections)
- `evidence` (list of paths or references)
- `insight_ref`
- `promotion_reason`

Key-event constraints:
- Key event should have at least one scope: `plan_id` or `topic_id`.
- Key event should include pointer evidence: `evidence` or `doc_refs`.

## L3: Insight Record (`docs/memory/insights/<event-id>.json`)

Required fields:
- `id`
- `event_id`
- `timestamp`

Optional high-value fields:
- `hypothesis`
- `attempt`
- `outcome`
- `lesson`
- `next_action`
- `evidence`

## Index (`docs/memory/MEMORY_INDEX.json`)

Required fields:
- `version`
- `schema_version`
- `created_at`
- `updated_at`
- `event_seq`
- `snapshot_seq`
- `event_count`
- `key_event_count`
- `last_event_id`
- `last_snapshot_id`
