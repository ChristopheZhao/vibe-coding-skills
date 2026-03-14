# Canonical Artifact Surfaces

Read stable artifact surfaces, not skill names.

## Plan Surface
- `docs/plans/PLAN_INDEX.json`
- `docs/plans/active/*.md`
- Prioritize:
  - current status
  - unchecked or unfinished items
  - `Execution Handoff`
  - evidence pointers

## Memory Surface
- `docs/memory/summary/current.json`
- `docs/memory/summary/current.md`
- When needed, follow refs into `events` or `insights`.

## Experience Surface
- `docs/experience/cards/*.json`
- Read only a small number of directly relevant cards or refs.

## Process/Evidence Surface
- Read process notes, test outputs, design docs, and logs that are already referenced by plan, memory, or experience docs.
- Keep references repo-relative whenever possible.

## Reading Priority
1. Related plan refs
2. Related memory refs
3. Related process/evidence refs
4. Related experience refs

## Rule
- If a project does not fully use one existing skill, but equivalent docs exist under these surfaces, `session-handoff` should still work.
