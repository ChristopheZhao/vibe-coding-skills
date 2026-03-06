# Retrieval Profiles

## Output Contract

`retrieve` returns a context pack with fixed top-level fields:
- `profile`
- `generated_at`
- `plan_id`
- `topic_id`
- `fallback_used`
- `state`
- `events`
- `insights`
- `next_actions`
- `contract`

## Profile Semantics

### `resume`
- Goal: continue interrupted work quickly.
- Event priority: `milestone`, `decision`, `blocker`, `fix`, `rollback`.
- Default limit: 8.

### `debug`
- Goal: avoid repeated failed attempts and recover troubleshooting context.
- Event priority: `blocker`, `experiment`, `rollback`, failed `fix`.
- Default limit: 10.

### `release`
- Goal: summarize high-signal readiness context.
- Event priority: key `milestone`, key `decision`, high-impact `fix`/`rollback`.
- Default limit: 6.

## Ranking Policy
- Prefer key events.
- Prefer matching scope (`plan_id` and/or `topic_id`).
- Prefer higher impact and profile-relevant event types.
- Prefer newer events when scores tie.

## Fallback Policy
- If no event passes strong-signal threshold, return:
  - current L1 state
  - latest high-priority/key L2 events
  - available next actions
- Mark `fallback_used=true`.
