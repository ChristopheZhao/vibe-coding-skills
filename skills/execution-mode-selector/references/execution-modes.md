# Execution Modes

## `one-shot`
Use when:
- scope is small
- core behavior is clear
- verification is local and cheap
- rollback cost is low

Do not use when:
- key architecture or contract choices are still unresolved
- the task crosses multiple risky surfaces

## `research-first`
Use when:
- the first blocker is missing information, not execution structure
- external docs, local code reading, or dependency behavior must be clarified before planning

Do not use when:
- the task is already well understood but simply large

## `discussion-first`
Use when:
- the main blocker is unresolved trade-off or high ambiguity
- multiple roles or perspectives are needed before planning
- architecture or product boundary choices are contested

Typical next owner:
- `multi-agent-discussion-advisor`

## `sprint-required`
Use when:
- the task is too large or risky for one continuous solo rollout
- verification should happen in multiple semantic closures
- one-shot execution would hide failure until too late

Output expectation:
- coarse sprint titles
- what each sprint closes
- why each boundary exists

Do not output:
- a detailed implementation checklist
- checkpoint verdicts
