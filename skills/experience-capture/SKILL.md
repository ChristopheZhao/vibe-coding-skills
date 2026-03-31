---
name: experience-capture
description: Capture reusable coding experience cards from key alignment and hard-problem resolution moments. Use when users ask to summarize lessons, preserve decision rules, or build reusable play patterns across tasks and projects. Do not use for next-window handoff, context offload, verbatim transcript archival, routine progress logging, or replacing layered project memory.
---

# Experience Capture

## Purpose
Use this skill to extract reusable engineering experience from high-signal moments.
The primary output is an experience card focused on decision rules, anti-patterns, and review checklists.
For complex multi-round work, add a concise companion source retrospective note under `docs/experience/sources/` and point the card to it.
The source note exists only to explain the turning points that produced the lesson; it is not a session handoff pack or continuity record.

## Activation Gate
Activate when any condition is true:
- User explicitly asks to summarize lessons,经验沉淀,复盘, or save reusable经验.
- User explicitly asks: "总结一下上面讨论的经验形成记录" / "形成经验记录" / "沉淀经验卡".
- A long multi-round alignment ends with clear consensus and transferable rules.
- A hard problem is resolved and includes decisions that can prevent future repeat mistakes.

Priority rules:
- Explicit user trigger has highest priority and must not be blocked by low-disturbance rules.
- Anti-trigger and cooldown rules apply only to `suggest-once` (automatic suggestion) path.

Do not activate when any condition is true:
- Work is a small one-off edit with no reusable pattern.
- Request is only status update or raw progress logging.
- Request is only verbatim transcript/raw diff archival without abstraction intent.

## Scope Limit
This skill manages reusable experience cards.
For complex captures, it may also create a short source retrospective note as evidence context for the card.
This skill does not:
- replace project state tracking in `layered-project-memory`
- replace Git commit/diff history
- implement runtime orchestration logic
- trigger high-frequency interruptions on every turn
- own session-level handoff/context offload for next-window continuation
- own full-fidelity project history archival or continuity memory across the entire project

## Ownership Boundary
- `layered-project-memory` owns project continuity memory (`state/events/insights`).
- `session-handoff` owns session-level continuation packs for next-window continuation.
- `experience-capture` owns cross-task reusable经验卡.
- For complex cases, `experience-capture` may own a concise source retrospective note in `docs/experience/sources/` as card evidence.
- Link by pointer (`source_event_refs`, `doc_refs`), do not duplicate large logs.
- If the user's real need is current-window handoff / context offload / next-window continuation, use `session-handoff` and only derive cards here when reusable lessons exist.
- If the user's real need is long-term project continuity / restore full project state, use `layered-project-memory` and only derive cards here when reusable lessons exist.

## Script Decision
Use the skill-bundled `scripts/exp_ops.py` (resolved relative to this skill root) for deterministic experience card initialization, creation, listing, and linking.
Avoid manual editing unless recovery is required.

## Workflow Contract
1. Detect trigger path:
   - `manual-explicit`: user clearly requests experience capture.
   - `suggest-once`: system proposes capture under hard gates.
2. `manual-explicit` path:
   - Enter extraction directly; do not apply cooldown/anti-trigger suppression.
3. `suggest-once` path:
   - Ask once whether to save reusable experience.
   - If user rejects, enter cooldown and stop.
4. Choose artifact shape:
   - `card-only`: default for clear reusable lessons with limited process complexity.
   - `dual-output`: when the work is complex enough to need a concise source note, but still centers on one main lesson cluster and its key turning points.
5. `dual-output` path:
   - Write a concise source retrospective note under `docs/experience/sources/`.
   - Capture only the minimum context needed to explain the lesson: background, key turning points/root cause, achieved state, and why the experience matters.
   - Keep it summary-level and pointer-first; do not dump full transcripts, routine progress logs, or next-window boot guidance.
6. Persist the card by `exp_ops.py create` and optional `link` references after user confirmation.
7. Reuse via `exp_ops.py list` with tags/signature filters.

## Hard Gates
- No write without user confirmation.
- Card must include `problem_signature`, `decision_rules`, and `review_checklist`.
- Card must contain at least one evidence pointer (`source_event_refs` or `doc_refs`).
- If `dual-output` is selected, the source retrospective note must stay concise and must not replace project memory or session handoff.
- Trigger logic is rule-based and explainable; no in-skill scoring engine.

## Resource Map
- Read `references/reference/positioning-boundary.md` for定位与边界.
- Read `references/reference/trigger-rules.md` for触发与反触发规则.
- Read `references/reference/process-protocol.md` for标准流程.
- Read `references/reference/card-schema.md` for经验卡字段契约.
- Read `references/reference/quality-gates.md` for低打扰质量约束.
- Read `references/reference/regression-cases.md` for触发与关联回归样例.
- Read `references/examples/README.md` for样例目录导航.
- Read `references/examples/*.md` for可复用经验样例与非样例.
- Use the skill-bundled `scripts/exp_ops.py` for managed operations.
