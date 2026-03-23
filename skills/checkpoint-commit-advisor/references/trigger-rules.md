# Trigger Rules

## Should Trigger
1. The worktree is large or mixed and the next phase is about to start.
2. The user asks whether to commit before a new plan, successor plan, or new window.
3. The user wants a checkpoint, WIP snapshot, governance anchor, or known-bad snapshot strategy.
4. Continuing without a checkpoint would blur old experiments and new refactor work.

## Should Not Trigger
1. The dirty tree is tiny and clearly scoped.
2. The user only asks for plan creation, plan status updates, or checkpoint validation.
3. The request is ordinary git usage, PR cleanup, or history rewriting.

## Guardrails
- Trigger on checkpoint-commit decision needs, not on every normal commit.
- Prefer not triggering over over-triggering when the dirty tree is small and obvious.
- If worktree corruption or ambiguity is detected, recommend `defer` instead of forcing a commit strategy.
