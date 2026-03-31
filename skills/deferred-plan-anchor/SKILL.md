---
name: deferred-plan-anchor
description: Maintain deferred but currently binding technical guardrails for long-horizon architecture direction, including independent deferred-plan artifacts, status management, and a narrow adapter that resolves whether current planning should inherit those guardrails. Use when a technical direction is intentionally deferred now but must still constrain near-term planning to prevent drift. Do not use for concrete execution planning, general backlog management, discussion-only evaluation, or project memory capture.
---

# Deferred Plan Anchor

## Purpose
Use this skill when a long-horizon technical direction is accepted in principle but intentionally deferred in implementation, and near-term planning still needs a durable guardrail so the codebase does not drift farther away from that direction.
The skill owns deferred-plan artifacts, lifecycle, and planning-resolution logic. It does not own execution plans.

## Activation Cues
Activate when any condition is true:
- The user says a technical migration or architecture direction is correct long-term but should not be executed now.
- The user wants to freeze "do not expand this workaround / dual-write / temporary authority" style guardrails before later refactor work.
- The user wants a deferred but active technical constraint recorded so future planning can reference it.
- The host workflow needs to resolve whether current planning should inherit an active deferred plan.

Do not activate when any condition is true:
- The request is to create or refine a concrete implementation plan for immediate execution.
- The request is only to discuss which architecture is better, without deciding a deferred-but-binding direction.
- The request is ordinary roadmap, backlog, or prioritization management.
- The request is project memory capture, reusable lesson capture, or session handoff.

## Scope Limit
This skill does:
- define and maintain deferred-plan artifacts under `docs/deferred-plans/`
- keep independent deferred-plan status truth and archive rules
- derive a concise current summary from the single active deferred plan
- resolve whether a planning request should inherit current deferred guardrails
- expose a narrow adapter for host workflows

This skill does not:
- own `docs/plans/PLAN_INDEX.json` or execution-plan lifecycle
- replace `sdd-plan-maintainer`
- decide the best architecture direction during discussion-only work
- become generic backlog or roadmap management
- become project memory or experience storage

## Ownership Boundary
- `multi-agent-discussion-advisor` owns discussion-phase convergence and advisory output.
- `sdd-plan-maintainer` owns execution-plan definition and lifecycle governance under `docs/plans/`.
- `layered-project-memory` owns durable continuity memory and must not become a second lifecycle truth.
- `deferred-plan-anchor` owns deferred but currently binding technical guardrails under `docs/deferred-plans/`.

Boundary rules:
- `deferred-plan-anchor` may expose planning guardrails to another skill or host workflow, but it must not mutate execution-plan lifecycle.
- `sdd-plan-maintainer` may consume externally supplied planning guardrails, but it must not discover, parse, or own deferred-plan artifacts.

## Script Decision
Use the skill-bundled `scripts/anchor_ops.py` (resolved relative to this skill root) for deterministic deferred-plan creation, status transitions, summary synchronization, doctor checks, and planning-resolution output.
Use the skill-bundled `scripts/smoke.sh` for structure and CLI-contract validation.

## Workflow Contract
1. Confirm the decision surface is a deferred-but-binding technical direction, not immediate execution planning.
2. Create or update a deferred plan with:
   - long-horizon goal
   - why it is deferred now
   - current deviation
   - current "do not expand" guardrails
   - allowed short-term actions
   - reopen trigger
3. Keep deferred-plan status under the independent deferred-plan index.
4. Derive `CURRENT.md` only from the unique `active` deferred plan.
5. When a host workflow explicitly asks whether planning should inherit deferred guardrails, run `resolve-for-planning`.
6. Return guardrails only when the deferred-plan system is enabled, exactly one plan is active, the active plan is not stale, and scope/topic inputs match.
7. Otherwise return a no-op planning result so the host can continue with normal planning.

## Hard Rules
- Never mutate `docs/plans/PLAN_INDEX.json`.
- Never treat deferred plans as generic backlog items.
- Keep v1 to at most one `active` deferred plan per repository.
- Only `active` deferred plans may affect `CURRENT.md` or planning resolution.
- `superseded`, `completed`, and `archived` plans must not continue influencing planning.
- The adapter must stay narrow: resolve applicability and current guardrails, not re-plan the work.

## Resource Map
- Read `references/positioning-boundary.md` for owner split and non-goals.
- Read `references/trigger-rules.md` for trigger and non-trigger cues.
- Read `references/process-protocol.md` for the deferred-plan workflow.
- Read `references/artifact-contract.md` for `docs/deferred-plans/` layout and state model.
- Read `references/output-contract.md` for the adapter return contract and summary expectations.
- Read `references/regression-cases.md` for stale-plan, trigger-boundary, and no-op regression checks.
- Read `references/examples/README.md` for positive and negative examples.
- Use the skill-bundled `scripts/anchor_ops.py` for deterministic operations.
- Use the skill-bundled `scripts/smoke.sh` for deterministic smoke checks.
