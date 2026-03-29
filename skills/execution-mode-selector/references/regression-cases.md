# Regression Cases

## Positive Cases
- A cross-cutting feature touches multiple skills and needs staged execution before validation can happen safely.
- The user asks whether work should be one-shot or split into sprints.
- The main blocker is architecture uncertainty and the right answer is `discussion-first`.

## Negative Cases
- A one-file typo fix with immediate local verification.
- A request to mark a managed plan `completed` or `blocked`.
- A request to run checkpoint validation or acceptance review on already-structured work.

## Boundary Cases
- The task is large but already has a confirmed sprint/checkpoint structure.
  - Expected result: do not re-run this skill unless the structure is being reconsidered.
- The task is ambiguous and also needs multi-role review.
  - Expected result: `discussion-first`, then hand off to `multi-agent-discussion-advisor`.
- The task is understood but too large for one-shot implementation.
  - Expected result: `sprint-required`, then hand off to `sdd-plan-maintainer`.
