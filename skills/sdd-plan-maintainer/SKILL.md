---
name: sdd-plan-maintainer
description: Create and maintain SDD execution plans for coding work, including concrete feature or fix planning, milestone status tracking, user-confirmed completion gates, archive or index synchronization under docs/plans, and optional harness state handoff without duplicating lifecycle ownership. Use when users ask for a specific plan, plan refinement, phased execution tracking, progress updates, or plan closure. Do not use for one-off tiny edits, pure Q and A, or internal scratch planning with no user-visible plan output.
---

# SDD Plan Maintainer

## Purpose
Use this skill for project-level planning and plan governance.
Produce concrete and actionable plans, then maintain lifecycle consistency when a plan is tracked across turns.

## Activation Gate
Activate when any condition is true:
- User asks for a concrete plan or a more specific plan for feature, fix, or refactor work.
- User asks to continue a plan, update plan status, or track phased progress.
- User asks to close a plan with completion confirmation or archive actions.

Do not activate when any condition is true:
- Request is pure Q and A, broad brainstorming, or unconstrained exploration.
- Work is a one-off tiny edit with no milestone or acceptance tracking need.
- User asks for direct implementation only and does not request planning or governance.

## Persistence Policy
Use one of three modes after activation:
- Temporary planning mode: produce or refine a plan in response text without file writes.
- Managed planning mode: create or update persistent assets under `docs/plans/` and synchronize `PLAN_INDEX.json`.
- Governance action mode: status transition, completion confirmation, and archive operations on managed plans.

Mode selection rules:
- Plan refinement requests can stay in Temporary planning mode unless durable tracking is requested.
- New long-running plans should enter Managed planning mode.
- Status updates or archive requests must use Governance action mode.

## Scope Limit
This skill manages plan definition and plan lifecycle state.
It does not replace normal coding orchestration, tool selection, or full long-running implementation control.
After each governance milestone, return to default Codex execution behavior.
It may reflect externally supplied planning guardrails in plan output, but it must not discover or own optional guardrail systems itself.

## Harness Fusion Boundary
Use a two-layer architecture to avoid overlap:
- Governance layer (this skill + the skill-bundled `scripts/plan_ops.py`, resolved relative to this skill root): plan lifecycle status, completion gates, archive, and index consistency.
- Execution layer (external harness): short-lived run context such as current focus, blockers, next action, and evidence pointers.

Boundary rules:
- Lifecycle status has a single owner: governance layer (`docs/plans/PLAN_INDEX.json` is the source of truth; plan header is a synced mirror).
- Execution layer must not introduce a second status machine.
- Governance notes should store milestone evidence, not full execution transcripts.
- Optional guardrail providers such as `deferred-plan-anchor` remain separate owners; this skill only consumes guardrails when another workflow explicitly supplies them.

## Script Decision
Use the skill-bundled `scripts/plan_ops.py` (resolved relative to this skill root) when lifecycle consistency or auditability is required.
Script usage is optional for Temporary planning mode.
If script is skipped, still follow `references/process-protocol.md`.

## Workflow Contract
1. Classify mode as `feature`, `fix`, or `execution`.
2. Select persistence mode by request intent.
3. If external planning guardrails are explicitly supplied, incorporate them into the plan without taking ownership of their source system.
4. Produce a concrete modular plan with priority and verification steps.
5. If harness integration is requested, define or refresh execution handoff pointers without changing lifecycle ownership.
6. If managed mode is active, ensure plan storage and index exist.
7. Update status only at meaningful milestones.
8. Gate completion by implementation evidence, testing, and user confirmation.
9. Archive only after confirmation and closed status.

## Hard Gates
- `completed` requires implementation done, tests passed, and user confirmation.
- `archived` requires user confirmation and an already closed plan (`completed` or `superseded`).
- `blocked` must include a concrete blocker note and next action.
- `superseded` requires a concrete note explaining why the plan direction was invalidated and what should be used instead.

## Resource Map
- Read `references/process-protocol.md` for activation and boundary policy.
- Read `references/activation-regression-cases.md` for trigger and non-trigger regression checks.
- Read `references/plan-templates.md` for plan content templates.
- Read `references/plan-ops-cookbook.md` for operation commands.
- Read `references/status-diff-worktree-guide.md` for status visibility, compare-file tracking, and optional worktree context.
- Read `references/harness-fusion-pattern.md` when integrating long-running execution harnesses.
- Use the skill-bundled `scripts/plan_ops.py` for deterministic plan lifecycle and index operations.
