# Positioning and Boundary

## Purpose
`execution-mode-selector` is the execution-shape selector for coding work before implementation starts.

It exists to answer:
- Can this be done safely in one shot?
- Should the host agent research first?
- Should the host agent run discussion first?
- Should the work be split into coarse sprints before planning/execution continues?

## Owner Split
- `execution-mode-selector`: execution shape and coarse sprint topology
- `sdd-plan-maintainer`: plan lifecycle truth and managed plan state
- `multi-agent-discussion-advisor`: pre-execution multi-role discussion
- `checkpoint-gatekeeper`: checkpoint verdicts and bounded remediation

## Non-goals
- task execution orchestration
- plan lifecycle mutation
- checkpoint or acceptance verdicts
- low-level implementation checklist generation
- memory, handoff, or experience persistence

## Boundary Rule
If the output already looks like a detailed task list, lifecycle plan, or checkpoint gate artifact, the skill has crossed its boundary.
