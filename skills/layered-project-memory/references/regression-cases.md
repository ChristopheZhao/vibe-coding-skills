# Regression Cases

## Case 1: Repeated Failure on Same Problem
- Input: two failed attempts with same `problem_key`.
- Expected:
  - later event gets higher key score
  - `debug` profile prioritizes later failed attempt
  - context pack includes relevant next action when provided

## Case 2: Strategy Switch
- Input: a decision event that changes implementation strategy, followed by milestone update.
- Expected:
  - `resume` profile returns strategy switch context near the top
  - pack includes state + next actions for handoff continuity

## Case 3: Interrupted Handoff Resume
- Input: milestone or blocker event with explicit `next_action`.
- Expected:
  - `resume` pack includes `next_actions` with actionable handoff item
  - fallback path still returns L1 + recent L2 when ranking signal is weak

## Case 4: Retention GC
- Input: event volume exceeds retention thresholds and multiple snapshots exist.
- Expected:
  - GC retains recent/key/referenced events
  - obsolete snapshots and orphan insights are pruned
  - `doctor` remains clean after GC

## Case 5: No-SDD Topic Scope
- Input: key events captured with `topic_id` only and pointer refs (`doc_ref`, `evidence`).
- Expected:
  - capture succeeds without `plan_id`
  - `retrieve` can scope by `topic_id`
  - pack returns pointer fields without duplicating large source content

## Case 6: Summary Incremental Compression
- Input: summary exists, then new high-signal events are captured under the same scope.
- Expected:
  - `summarize --mode incremental` updates summary using only new events since the last anchor
  - `last_event_seq` and `last_event_id` advance monotonically
  - summary keeps pointer-first highlights and next-actions without creating independent facts

## Case 7: Summary Rebuild Recovery
- Input: stale/corrupted summary anchor (`last_event_id` missing in events).
- Expected:
  - `summarize --mode incremental` falls back to rebuild behavior
  - regenerated summary remains consistent with current scoped memory
