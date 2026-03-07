# Trigger Rules

## Trigger Matrix

| Scenario | Trigger | Action |
| --- | --- | --- |
| User asks to continue previous work | Yes | `retrieve --profile resume` |
| Repeated failure on same problem | Yes | `capture` + optional `promote` + `retrieve --profile debug` |
| Milestone decision/rollback/blocker | Yes | `capture` + `summarize --mode incremental` + `doctor` |
| Release readiness summary request | Yes | `retrieve --profile release` |
| One-off tiny edit with no continuity | No | Skip memory persistence |
| Pure Q and A / brainstorming | No | Skip memory persistence |
| Raw transcript archival request | No | Reject overlap, keep boundary |
| Routine turn-by-turn coding chat | No | Do not write memory every turn |

## Non-Trigger Regression Set
- Tiny one-file typo fix.
- Translation or wording rewrite.
- General architecture chat without implementation.
- Request to dump full chat logs into memory storage.

## Escalation Rules
- Missing scope on key event: require `plan_id` or `topic_id`.
- Missing Git anchors in a Git repository: mark issue in `doctor`.
- Ambiguous profile: default to `resume` and annotate in output metadata.

## Frequency Budget
- Prefer 1-2 writes per meaningful stage, not per chat turn.
- Skip capture when no new decision/failure/turning-point signal exists.
- Run summary compression at key transitions, not every turn.
