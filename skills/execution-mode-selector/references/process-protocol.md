# Process Protocol

## 1. Frame the Task
Capture:
- goal
- scope
- constraints
- unknowns
- verification burden
- rollback cost

## 2. Check Risk Signals
Look for:
- cross-module coupling
- unresolved contracts
- uncertain feasibility
- delayed validation
- expensive rollback

## 3. Select the Minimum Sufficient Mode
Choose exactly one:
- `one-shot`
- `research-first`
- `discussion-first`
- `sprint-required`

The chosen mode must be justified against at least one plausible alternative.

## 4. Emit Coarse Topology When Needed
Only for `sprint-required`:
- 2-5 coarse sprints
- each sprint closes one semantic slice
- each sprint includes a `why this boundary exists` line

## 5. Hand Off Cleanly
- planning next -> `sdd-plan-maintainer`
- discussion next -> `multi-agent-discussion-advisor`

Do not continue into lifecycle mutation, checkpoint definition, or acceptance review inside this skill.
