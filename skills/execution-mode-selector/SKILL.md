---
name: execution-mode-selector
description: Decide whether a coding task should run as one-shot, research-first, discussion-first, or sprint-required before execution starts, and provide coarse sprint topology with rationale when one-shot execution is too risky. Use when task complexity, uncertainty, cross-module coupling, or verification cost suggests continuous solo execution may be unsafe. Do not use for plan lifecycle updates, checkpoint validation, final acceptance review, or runtime orchestration.
---

# Execution Mode Selector

## Purpose
Use this skill before execution starts to choose the minimum sufficient execution shape for a coding task.
The output is a mode verdict plus rationale, and when needed, a coarse sprint topology that explains why the task should not be run as one continuous solo rollout.
This skill works at task level: it decides how the whole task should run, not what counts as done for one chosen sprint or slice.

## Activation Gate
Activate when any condition is true:
- The task spans multiple modules, interfaces, or execution stages.
- Verification cost is high enough that failure would be discovered late.
- Core requirements, architecture, or feasibility are still uncertain.
- The user asks whether the task should be split into sprints, done in one shot, or discussed first.
- The host agent is about to start a long-running task and needs an execution-shape decision first.

Do not activate when any condition is true:
- The request is a tiny, obvious edit with local verification and low rollback cost.
- The work is already inside managed execution with a confirmed sprint/checkpoint structure.
- The user is asking to update plan lifecycle state, run checkpoint validation, or perform final acceptance review.

## Scope Limit
This skill does:
- execution-shape selection before implementation starts
- coarse sprint topology for `sprint-required` cases
- rationale for why one-shot execution is safe or unsafe
- handoff recommendation to the next owner skill

This skill does not:
- own `docs/plans/PLAN_INDEX.json` lifecycle state
- produce checkpoint verdict artifacts
- perform plan execution or runtime orchestration
- replace task-specific acceptance review
- emit low-level execution checklists

## Ownership Boundary
- `sdd-plan-maintainer` owns plan lifecycle truth and managed plan state.
- `checkpoint-gatekeeper` owns checkpoint verdicts and bounded remediation loops.
- `multi-agent-discussion-advisor` owns discussion-phase multi-role synthesis when discussion is required.
- `execution-mode-selector` owns only the pre-execution decision surface: which execution mode to use, and why.

Boundary rule:
- Keep sprint topology coarse and strategy-level.
- If the next step is planning, hand off to `sdd-plan-maintainer`.
- If the next step is discussion, hand off to `multi-agent-discussion-advisor`.
- If a sprint or work slice already exists and only its completion contract is missing, route to `execution-contract-designer` instead of re-running execution-shape selection.

## Script Decision
Use `scripts/smoke.sh` for structure and contract checks only.
No business runtime script is required in v1.

## Workflow Contract
1. Frame the task: goal, scope, constraints, unknowns, and verification burden.
2. Check complexity signals, uncertainty signals, and rollback cost.
3. Select one verdict:
   - `one-shot`
   - `research-first`
   - `discussion-first`
   - `sprint-required`
4. Explain why the chosen mode is safer than the main alternatives.
5. If the verdict is `sprint-required`, provide a coarse sprint topology:
   - sprint title
   - what this sprint closes
   - why this boundary exists
6. Point to the next owner skill:
   - `sdd-plan-maintainer` for managed planning
   - `multi-agent-discussion-advisor` for pre-execution discussion

## Hard Rules
- Do not create or mutate plan lifecycle state.
- Do not emit checkpoint or acceptance verdicts.
- Do not decompose into low-level implementation tasks.
- When choosing anything other than `one-shot`, explain why one-shot execution is unsafe.
- Prefer the minimum sufficient harness: do not recommend sprints or discussion when a one-shot path is clearly safe.
- Keep trigger logic cue-based and explainable; do not build a hidden scoring engine into the skill contract.

## Resource Map
- Read `references/positioning-boundary.md` for layer split and non-goals.
- Read `references/trigger-rules.md` for activation and anti-trigger rules.
- Read `references/execution-modes.md` for mode definitions and comparison guidance.
- Read `references/process-protocol.md` for the decision sequence.
- Read `references/output-contract.md` for output fields and verdict schema.
- Read `references/regression-cases.md` for trigger-boundary regression expectations.
- Read `references/examples/README.md` for positive and negative examples.
- Use `scripts/smoke.sh` for deterministic smoke checks.
