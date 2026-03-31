---
name: layered-project-memory
description: Capture and retrieve layered project memory for coding projects, including project state (L1), key events (L2), and node insights (L3) with Git anchors and pointer-first evidence links. Use when users ask to resume interrupted work, preserve key milestone context, avoid repeated failed attempts, or generate focused context packs for resume/debug/release workflows. Do not use for one-off tiny edits, pure Q and A, or full transcript archival.
---

# Layered Project Memory

## Purpose
Use this skill as a project semantic memory layer for high-signal context.
Persist only information that Git and agent short-term memory do not store directly.
Keep continuity across interrupted sessions, repeated attempts, and handoffs.

## Activation Gate
Activate when any condition is true:
- User asks to resume previous coding work, handoff context, or recover project state.
- Work involves repeated attempts on the same issue and needs anti-repeat memory.
- Milestone transition, decision, blocker, rollback, or key fix needs persistent evidence.
- User asks for focused context packs for `resume`, `debug`, or `release`.

Do not activate when any condition is true:
- Request is a one-off tiny edit with no continuity need.
- Request is pure Q and A or unconstrained brainstorming.
- Request asks for full transcript archival or raw diff storage.

## Scope Limit
This skill manages layered memory:
- L1 project state
- L2 key event index
- L3 node insight records
- derived summary for fast context loading

This skill does not:
- replace Git commit/diff history
- replace SDD lifecycle ownership when SDD is in use
- archive full chat transcripts or source snapshots
- write memory on every turn (low-frequency trigger only)

## Ownership Boundary
- Git owns code facts (`commit`, `diff`, file content).
- SDD owns plan lifecycle status under `docs/plans/` when the project uses SDD.
- This skill owns `why/tried/learned/next` memory under `docs/memory/`.

Boundary rules:
- L2/L3 records must include Git anchors and at least one scope (`plan_id` or `topic_id`) for key events.
- Retrieval output is pointer-first: reference evidence/doc links and avoid duplicating raw deltas.
- Memory must not introduce a second lifecycle status machine.
- Summary is derived from memory records; it is not a second source of truth.

## Script Decision
Use the skill-bundled `scripts/memory_ops.py` (resolved relative to this skill root) for deterministic storage, retrieval, and consistency checks.
Avoid manual editing of memory artifacts unless recovery is required.

## Workflow Contract
1. Classify request as `capture`, `resume`, `debug`, `release`, or `handoff`.
2. Ensure storage with `memory_ops.py init`.
3. Record key memory events with `capture` (not every turn) and optional insight fields.
4. Refresh derived summary with `summarize --mode <incremental|rebuild>` at key milestones.
5. Build context packs using `retrieve --profile <resume|debug|release>`.
6. Run `doctor` before handoff or after meaningful milestones.
7. Use `promote/snapshot/gc` only when extra governance is needed.

## Hard Gates
- Key events require `event_type`, `summary`, Git anchors, and scope (`plan_id` or `topic_id`).
- Key events should include pointer evidence via `evidence` or `doc_refs`.
- `summarize` output must be derived from L1/L2/L3; no independent facts in summary.
- `retrieve` output must follow `references/retrieval-profiles.md`.
- If retrieval signal is weak, return fallback pack (L1 + recent high-signal L2), never an empty pack.

## Resource Map
- Read `references/process-protocol.md` for execution protocol and command flow.
- Read `references/trigger-rules.md` for trigger/non-trigger matrix.
- Read `references/schemas.md` for L1/L2/L3 schema rules.
- Read `references/retrieval-profiles.md` for profile contracts and ranking policy.
- Read `references/regression-cases.md` for regression expectations.
- Use the skill-bundled `scripts/memory_ops.py` for managed operations.
