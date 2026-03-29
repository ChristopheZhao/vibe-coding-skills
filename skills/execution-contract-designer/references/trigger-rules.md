# Trigger Rules

## Activation Signals
Trigger when at least one signal is true:
- A coarse sprint exists but done criteria are still vague.
- Later review or checkpoint logic would be generic without task-specific criteria.
- The user asks for a contract, completion definition, evidence list, or checkpoint mapping for one work slice.
- A planning surface is aligned, but downstream evaluation would otherwise be ambiguous.

## Non-activation Signals
Do not trigger when any signal is true:
- The main question is whether the task should be one-shot, researched first, discussed first, or sprinted.
- The work still needs high-level requirement or architecture discussion.
- The request is to move plan status or emit a checkpoint verdict.
- The request is to perform acceptance review instead of define its input contract.

## Priority Rules
1. Use this skill only after execution shape is known.
2. Prefer one contract per sprint or semantic work slice.
3. Keep contract fields task-specific; reject generic boilerplate.
4. If a negative case cannot be named, the contract is probably underspecified.

## Anti-patterns
- Rewriting the plan as a contract without adding evaluability.
- Producing a universal checklist that could fit any task.
- Smuggling verdict decisions into the contract layer.
