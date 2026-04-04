---
name: checkpoint-gatekeeper
description: Enforce checkpoint-level verification before multi-phase work advances, using bounded auto-remediation and explicit escalation when failures are ambiguous or risky. Use when complex work should not proceed to the next stage without validating the current stage, including acceptance-oriented checkpoint profiles that still stay under checkpoint verdict ownership. Do not use for plan lifecycle ownership, session handoff, or full long-running orchestration.
---

# Checkpoint Gatekeeper

## Purpose
Use this skill to stop unverified stage output from leaking into later stages of complex work.
The skill provides a checkpoint-scoped verification and remediation loop: validate, optionally auto-fix within the current checkpoint, revalidate, then emit an explicit gate verdict.

## Activation Cues
Activate when any condition is true:
- The work is split into phases or checkpoints and the next phase should not start without verification.
- The user explicitly asks for checkpoint gating, stage validation, or a "do not proceed until verified" rule.
- A complex refactor or migration has high risk of error propagation across phases.
- The user wants a stage or final acceptance check that should stay under checkpoint verdict ownership.

Do not activate when any condition is true:
- The task is a one-off tiny edit with no phase boundary or checkpoint concept.
- The request is only to create or maintain a plan lifecycle state.
- The task needs full long-running orchestration across the entire project rather than one checkpoint-scoped gate loop.

## Scope Limit
This skill does:
- checkpoint-scoped validation and bounded auto-remediation
- checklist and gate artifact generation under `docs/checkpoints/`
- acceptance-oriented checkpoint profiles that assess semantic completion while staying under checkpoint ownership
- verdict emission: `pending`, `pass`, `auto_fixed_pass`, `fail`, `needs_user_confirmation`, `waived`

This skill does not:
- own `docs/plans/PLAN_INDEX.json` lifecycle state
- archive, complete, or supersede plans
- perform silent waivers or silent gate-standard changes
- become a general long-running Ralph-style task loop in MVP

## Ownership Boundary
- `sdd-plan-maintainer` owns plan definition, lifecycle governance, and `docs/plans/PLAN_INDEX.json`.
- `checkpoint-gatekeeper` owns checkpoint verification artifacts and verdicts under `docs/checkpoints/`.
- `session-handoff` owns next-window continuation context, not gate verdicts.

Boundary rule:
- Gate verdicts are not plan lifecycle statuses.
- This skill may read plan checkpoints for linkage, but it must not mutate plan lifecycle state.

## Script Decision
Use the skill-bundled `scripts/gate_ops.py` (resolved relative to this skill root) for deterministic artifact creation, validation loops, verdict writing, and waiver handling.
Use the skill-bundled `scripts/smoke.sh` for structure and minimal CLI-contract checks.

## Workflow Contract
1. Confirm the target `plan_id` and `checkpoint`.
2. Confirm whether the checkpoint uses the default validation profile or an `acceptance` profile.
3. Create or refresh checklist and gate artifacts under `docs/checkpoints/<PLAN-ID>/`.
4. For `acceptance`, prepare the evidence artifact that captures contract linkage, changed artifacts, and executor-side evidence references.
5. Run validation commands for the checkpoint.
6. If validation fails and the checklist allows it, run bounded current-checkpoint remediation commands, then revalidate.
7. For formal `acceptance` verification, require an independent acceptance review artifact. Executor-side self-check may inform the evidence artifact, but it does not satisfy the review requirement by itself.
8. Emit one verdict:
   - `pass`
   - `auto_fixed_pass`
   - `fail`
   - `needs_user_confirmation`
   - `waived`
9. Escalate only when the result is ambiguous, risky, or would require a scope/standard change.

## Hard Rules
- Never mutate `docs/plans/PLAN_INDEX.json`.
- Never silently change checkpoint requirements or pass criteria.
- Never silently waive a checkpoint.
- Keep auto-remediation bounded to the current checkpoint and explicit remediation commands.
- If high-risk or ambiguous signals appear, emit `needs_user_confirmation` instead of forcing a pass.
- `acceptance` profile must remain a checkpoint profile, not a new lifecycle or verdict owner.
- Formal `acceptance` verification must consume an independent review artifact; executor self-check alone cannot produce a passing acceptance verdict.

## Resource Map
- Read `references/positioning-boundary.md` for scope and layer split.
- Read `references/trigger-rules.md` for trigger and non-trigger rules.
- Read `references/process-protocol.md` for the checkpoint verification loop.
- Read `references/artifact-contract.md` for `docs/checkpoints/<PLAN-ID>/` artifact layout and checklist marker format.
- Read `references/remediation-policy.md` for auto-fix boundaries and escalation conditions.
- Read `references/output-contract.md` for verdict semantics and gate artifact fields.
- Read `references/regression-cases.md` for trigger-boundary and no-overlap regression cases.
- Read `references/examples/README.md` for positive and negative examples.
- Use the skill-bundled `scripts/gate_ops.py` for deterministic gate operations.
- Use the skill-bundled `scripts/smoke.sh` for deterministic smoke checks.
