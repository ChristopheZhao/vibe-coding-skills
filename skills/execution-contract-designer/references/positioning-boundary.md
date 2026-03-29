# Positioning and Boundary

## Purpose
`execution-contract-designer` is the contract bridge between coarse planning and later evaluation surfaces.

It exists to answer:
- What exactly does this sprint or work slice close?
- Why is this a valid semantic boundary?
- What evidence should later checkpoints or acceptance consume?

## Owner Split
- `execution-mode-selector`: execution shape and coarse sprint topology
- `execution-contract-designer`: evaluable contract for one work slice
- `sdd-plan-maintainer`: managed plan lifecycle and status truth
- `checkpoint-gatekeeper`: checkpoint verdicts and bounded remediation

## Non-goals
- mode selection
- lifecycle mutation
- checkpoint or acceptance verdicts
- low-level implementation checklist ownership
- runtime orchestration

## Boundary Rule
If the output already looks like a plan status update, checkpoint verdict artifact, or task-by-task implementation list, the skill has crossed its boundary.
