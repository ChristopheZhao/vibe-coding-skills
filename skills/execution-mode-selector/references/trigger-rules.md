# Trigger Rules

## Activation Signals
Trigger when at least one signal is true:
- The task spans multiple modules, interfaces, or work phases.
- Key feasibility, architecture, or contract questions are unresolved.
- Verification would happen late, after several changes have already landed.
- Rollback cost is high if the first attempt is wrong.
- The user explicitly asks whether the work should be done in one shot, split into sprints, researched first, or discussed first.

## Non-activation Signals
Do not trigger when any signal is true:
- The request is a tiny change with local verification and low uncertainty.
- The task already has a confirmed managed sprint/checkpoint structure.
- The user is asking for plan lifecycle updates, checkpoint validation, or final acceptance review.

## Priority Rules
1. Explicit user ask about execution shape or sprinting triggers immediately.
2. High uncertainty or late verification risk should bias away from `one-shot`.
3. Prefer `one-shot` when the task is small, obvious, and easily reversible.
4. Prefer the minimum sufficient harness; do not add discussion or sprinting without a concrete reason.

## Anti-patterns
- Treating every non-trivial task as `sprint-required`.
- Confusing `research-first` with open-ended planning drift.
- Using `discussion-first` when the real need is only detailed execution planning.
- Returning a full execution checklist instead of a coarse topology.
