---
name: experience-capture
description: Capture reusable coding experience cards from key alignment and hard-problem resolution moments. Explicit user requests like "总结一下上面讨论的经验形成记录" should trigger this skill with high priority. Use when users ask to summarize lessons, preserve decision rules, or build reusable play patterns across projects. Do not use for verbatim transcript archival, routine progress logging, or replacing layered project memory.
---

# Experience Capture

## Purpose
Use this skill to extract reusable engineering experience from high-signal moments.
The output is an experience card focused on decision rules, anti-patterns, and review checklists.

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
This skill does not:
- replace project state tracking in `layered-project-memory`
- replace Git commit/diff history
- implement runtime orchestration logic
- trigger high-frequency interruptions on every turn

## Ownership Boundary
- `layered-project-memory` owns project continuity memory (`state/events/insights`).
- `experience-capture` owns cross-task reusable经验卡.
- Link by pointer (`source_event_refs`, `doc_refs`), do not duplicate large logs.

## Script Decision
Use `scripts/exp_ops.py` for deterministic experience card initialization, creation, listing, and linking.
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
4. Persist by `exp_ops.py create` and optional `link` references after user confirmation.
5. Reuse via `exp_ops.py list` with tags/signature filters.

## Hard Gates
- No write without user confirmation.
- Card must include `problem_signature`, `decision_rules`, and `review_checklist`.
- Card must contain at least one evidence pointer (`source_event_refs` or `doc_refs`).
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
- Use `scripts/exp_ops.py` for managed operations.
