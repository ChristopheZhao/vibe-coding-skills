---
name: session-handoff
description: Create a session-level continuation pack when the current coding window should offload context before continuing in a new window. Use when users ask to整理当前 session, prepare a new window to continue the same unfinished task, or create a handoff/context-offload summary from current progress, blockers, plans, memory, and lessons. Do not use for reusable experience capture, standalone plan updates, or full transcript archival.
---

# Session Handoff

## Purpose
Use this skill to offload the current session into a continuation pack before opening a new window for the same unfinished task.
The primary output is one Markdown handoff file under `docs/session-handoff/` that helps the next window quickly recover task state, blockers, next action, and relevant lessons without manually rebuilding context.

## Activation Cues
Activate when any condition is true:
- User explicitly asks to整理当前 session, 做 handoff, 做 context offload, or prepare a new window to continue the same task.
- The current task is unfinished and the user wants a session-level summary for next-window continuation.
- User asks to summarize what this window has done, what remains, and what the next window should read first.

Do not activate when any condition is true:
- The request is only to create reusable lessons or an experience card.
- The request is only to update plan status or lifecycle governance.
- The request is only to preserve long-term project memory without a window handoff need.
- The request is full transcript archival or raw chat export.

## Scope Limit
This skill manages session-level continuation packs.
This skill does:
- summarize current-session progress for next-window continuation
- aggregate high-signal refs from plans, memory, experience, and process docs
- preserve blockers, next actions, and avoid-repeat guidance
- point the next window to the right execution entrypoint before coding when direct coding would be unsafe

This skill does not:
- own plan lifecycle status
- own reusable experience-card persistence
- own project memory truth
- archive full chat transcripts
- auto-write back to plan, memory, or experience docs in MVP
- author or refresh implementation plans itself

## Ownership Boundary
- `sdd-plan-maintainer` owns plan lifecycle and plan status truth under `docs/plans/`.
- `layered-project-memory` owns continuity facts under `docs/memory/`.
- `experience-capture` owns reusable cross-task experience under `docs/experience/`.
- `session-handoff` owns session-level aggregation for next-window continuation.

Boundary rule:
- Read canonical artifact surfaces under `docs/` rather than depending on a specific skill name or output.
- Treat plan, memory, and experience docs as source of truth; the handoff pack is only a pointer-first aggregation layer.
- If a next-window plan review or plan creation should happen before coding, point to the right owner and current entrypoint, but do not write the plan content here.

## Script Decision
Use the skill-bundled `scripts/smoke.sh` for structure and contract checks only.
No business runtime script is required in MVP.

## Workflow Contract
1. Confirm the request is a current-window offload for same-task continuation.
2. Collect related plan, memory, experience, and process refs from `docs/` and other referenced evidence files.
3. Write one handoff pack to `docs/session-handoff/SHO-YYYYMMDD-NNNN.md`.
4. Keep the pack pointer-first and scoped to the current session, even when the session spans multiple subtasks.
5. Ensure the pack includes fixed sections:
   - `Session ID`
   - `Generated At`
   - `Offload Reason`
   - `Session Goal`
   - `Overview`
   - `Related Refs`
   - `Subtask Snapshots`
   - `Avoid Repeat`
   - `Next Window Boot`
   - `Source of Truth`
6. Limit `Avoid Repeat` to 1-3 high-signal items.
7. New-window consumption order must be stated clearly:
   - read `Offload Reason` and `Overview`
   - read `Subtask Snapshots`
   - read related plan refs
   - read related memory refs
   - read related experience refs and `Avoid Repeat`
   - then start new planning
8. When direct coding would be unsafe, add one concise `Before coding` hint inside `Next Window Boot` that points to the current execution entrypoint or the next planning owner.
   Keep it pointer-first; do not turn the handoff into a plan or execution contract.

## Hard Rules
- MVP is explicit-trigger only; no `suggest-once`.
- Output exactly one Markdown continuation pack per trigger.
- Do not create `.json` sidecars or `SESSION_INDEX.json` in MVP.
- Do not auto-refresh or mutate plan, memory, experience, or process docs in MVP.
- Keep references repo-relative whenever possible.
- Do not copy large logs or long document excerpts; summarize and point.
- If the current session invalidates an older plan, mark that plan as historical or reference-only in the pack and point to the new diagnostic entry, but do not mutate plan lifecycle state in this skill.
- Do not author plan steps, acceptance criteria, or execution contracts inside the handoff pack; only point to the next planning owner when needed.

## Resource Map
- Read `references/positioning-boundary.md` for scope and layer split.
- Read `references/trigger-rules.md` for trigger and non-trigger rules.
- Read `references/canonical-surfaces.md` for artifact-surface reading rules.
- Read `references/process-protocol.md` for execution flow and handoff order.
- Read `references/output-contract.md` for Markdown section contract.
- Read `references/resume-entrypoint-guidance.md` when the next window may need a plan review or a plan refresh before coding.
- Read `references/regression-cases.md` for trigger-boundary regression checks.
- Read `references/examples/README.md` for examples and non-examples.
- Use the skill-bundled `scripts/smoke.sh` for deterministic smoke checks.
