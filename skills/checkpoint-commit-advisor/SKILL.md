---
name: checkpoint-commit-advisor
description: Advise whether a dirty worktree should be checkpoint-committed before complex work moves to a new phase, new plan, or new window. Use when unfinished implementation, mixed changes, or large dirty trees need a clear checkpoint commit strategy with explicit layering such as governance anchor and known-bad snapshot. Do not use for plan lifecycle ownership, checkpoint validation, session handoff generation, or generic git history management.
---

# Checkpoint Commit Advisor

## Purpose
Use this skill when complex work should not continue on top of a noisy dirty worktree without first deciding whether to freeze the current state as one or more checkpoint commits.
The skill provides a commit-strategy advisory loop: inspect worktree state, decide whether to commit now or defer, propose one or more commit layers, and require explicit user confirmation before any real git write.

## Activation Cues
Activate when any condition is true:
- A large or mixed dirty worktree exists and the next phase is about to begin.
- The user asks whether to commit before opening a new plan, successor plan, or new window.
- The user asks for a checkpoint commit, WIP snapshot, governance anchor, or known-bad snapshot strategy.
- A long refactor is about to touch the same core files that are already dirty.

Do not activate when any condition is true:
- The task is a one-off tiny edit with a small, obvious worktree.
- The request is only to create or update a plan lifecycle state.
- The request is to validate a checkpoint or stage gate rather than decide commit strategy.
- The request is generic git history work such as rebase, squash, cherry-pick, amend, or force-push.

## Scope Limit
This skill does:
- checkpoint commit strategy analysis for dirty worktrees
- proposal of one-layer, two-layer, or three-layer checkpoint commit plans
- file bucketing, message planning, and confirmation-point output
- lightweight deterministic git-state inspection through a local analysis script

This skill does not:
- own `docs/plans/PLAN_INDEX.json` lifecycle state
- own checkpoint validation or auto-remediation verdicts
- generate session handoff packs
- guarantee code correctness
- silently execute `git add` or `git commit`
- become a generic git workflow or history-rewrite assistant

## Ownership Boundary
- `sdd-plan-maintainer` owns plan definition and lifecycle governance.
- `checkpoint-gatekeeper` owns checkpoint validation and gate verdicts.
- `session-handoff` owns next-window continuation packs.
- `layered-project-memory` owns durable project memory and may later consume commit anchors.
- `checkpoint-commit-advisor` owns the decision surface: whether to freeze the current dirty worktree now, and how to layer that checkpoint commit strategy.

Boundary rule:
- This skill may read plan or handoff context for labeling, but it must not mutate plan lifecycle or produce a second truth source.
- The default output is advisory. Real git writes require explicit user confirmation.

## Script Decision
Use `scripts/commit_advisor.py` for deterministic dirty-tree analysis and proposal output.
Use `scripts/smoke.sh` for structure and minimal CLI-contract checks.

## Workflow Contract
1. Inspect the dirty worktree and collect health signals.
2. Decide whether checkpoint commit strategy is warranted now or should be deferred.
3. If warranted, propose one-layer, two-layer, or three-layer commit structure.
4. For each proposed layer, list file buckets, commit intent, and suggested message.
5. Surface risks and confirmation points.
6. Only after explicit user confirmation should the host agent translate the proposal into real `git add` / `git commit` actions.

## Hard Rules
- Never silently stage or commit changes.
- Never present a checkpoint commit as proof of correctness.
- Treat “wrong but explainable” as acceptable for snapshot commits; treat corrupted or ambiguous worktree state as a blocker.
- Keep heuristics explainable and conservative.
- Avoid overlap with lifecycle, gate, handoff, or memory ownership.

## Resource Map
- Read `references/positioning-boundary.md` for the layer split and non-goals.
- Read `references/trigger-rules.md` for trigger and non-trigger signals.
- Read `references/process-protocol.md` for the advisory workflow.
- Read `references/output-contract.md` for output schema and commit-layer semantics.
- Read `references/regression-cases.md` for trigger-boundary and blocking regression cases.
- Read `references/examples/README.md` for positive and negative examples.
- Use `scripts/commit_advisor.py` for deterministic advisory output.
- Use `scripts/smoke.sh` for deterministic smoke checks.
