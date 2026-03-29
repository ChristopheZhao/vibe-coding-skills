---
name: execution-contract-designer
description: Turn a coarse sprint or planned work slice into an evaluable execution contract before implementation or stage validation begins, including what the sprint closes, why the boundary exists, done signals, evidence checklist, negative cases, and suggested checkpoints. Use when planning direction is already aligned but downstream review, checkpoint, or acceptance needs task-specific criteria. Do not use for lifecycle updates, checkpoint verdict execution, or final acceptance review itself.
---

# Execution Contract Designer

## Purpose
Use this skill after execution shape is known and before implementation or stage validation begins.
The output is an execution contract that turns a coarse sprint or work slice into something downstream review, checkpoint, and acceptance surfaces can evaluate without falling back to generic review.
This skill works at slice level: it defines what one chosen sprint or work slice must close, not whether the whole task should be one-shot or sprinted.

## Activation Gate
Activate when any condition is true:
- The task already has a coarse sprint or work-slice boundary but lacks explicit done criteria.
- The user asks to define what a sprint closes, what counts as done, or what evidence later gates should require.
- Downstream validation would otherwise rely on generic review because task-specific criteria are missing.
- A plan is directionally aligned, but checkpoints or acceptance would be ambiguous without a contract bridge.

Do not activate when any condition is true:
- The request is only to choose one-shot vs research vs discussion vs sprinting.
- The request is to update plan lifecycle state or checkpoint verdict state.
- The task is still blocked on high-level architecture or product ambiguity that should be discussed first.
- The request is to perform final acceptance review rather than define the contract it should use.

## Scope Limit
This skill does:
- contract authoring for a sprint or work slice
- task-specific done signals
- evidence checklist design
- negative-case capture
- suggested checkpoint mapping

This skill does not:
- own `docs/plans/PLAN_INDEX.json`
- emit checkpoint or acceptance verdicts
- replace execution-mode selection
- generate low-level implementation task lists
- execute review, validation, or remediation steps

## Ownership Boundary
- `execution-mode-selector` decides execution shape and whether sprinting is needed.
- `sdd-plan-maintainer` owns managed plan lifecycle and status truth.
- `checkpoint-gatekeeper` owns checkpoint verdicts and bounded remediation.
- `execution-contract-designer` owns only the contract layer between planning and evaluation.

Boundary rule:
- Keep the contract semantic and evaluable.
- Do not mutate lifecycle state or gate verdict artifacts.
- If the task still needs mode selection, route back to `execution-mode-selector`.
- If the task still needs high-level architecture or product alignment, route to `multi-agent-discussion-advisor` before writing a slice contract.

## Script Decision
Use `scripts/smoke.sh` for structure and contract checks only.
No business runtime script is required in v1.

## Workflow Contract
1. Frame the work slice: what it is supposed to close and why this boundary exists.
2. Define the semantic closure for the slice.
3. Write task-specific contract fields:
   - `what`
   - `why`
   - `done signals`
   - `evidence checklist`
   - `negative cases`
4. Suggest downstream checkpoints that later owners can evaluate.
5. Point to the next owner surface:
   - `sdd-plan-maintainer` if managed planning still needs to be updated
   - `checkpoint-gatekeeper` if checkpoint verification should consume the contract later

## Hard Rules
- Do not create or mutate plan lifecycle state.
- Do not emit checkpoint or acceptance verdicts.
- Do not collapse the contract into a generic review checklist.
- Do not decompose into low-level implementation tasks.
- Every contract must explain why the work slice boundary exists.
- Every contract must include at least one task-specific negative case.

## Resource Map
- Read `references/positioning-boundary.md` for layer split and non-goals.
- Read `references/trigger-rules.md` for activation and anti-trigger rules.
- Read `references/contract-fields.md` for field definitions and quality bar.
- Read `references/process-protocol.md` for the contract-authoring sequence.
- Read `references/output-contract.md` for output schema and examples.
- Read `references/regression-cases.md` for trigger-boundary regression expectations.
- Read `references/examples/README.md` for positive and negative examples.
- Use `scripts/smoke.sh` for deterministic smoke checks.
