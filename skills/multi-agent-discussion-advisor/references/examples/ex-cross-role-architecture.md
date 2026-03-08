# Example: Cross-role Architecture Trade-off (Template)

## Scenario Signals
- Architecture option A and B have conflicting implications.
- Decision spans multiple layers and teams.

## Parameterized Inputs
- Decision topic: `[architecture_topic]`
- Trade-off axes: `[quality | speed | complexity | maintainability]`
- Risk horizon: `[short_term | long_term]`

## Suggested Pattern
- Pattern: `Triad Trade-off`
- Candidate roles: `[architect] + [backend] + [frontend]`
- Optional role: `[product]` when user-value boundary is still unclear

## Advisory Output Skeleton
- Recommended pattern and reason:
- Role -> uncertainty mapping:
- Must-confirm checkpoints:
- Execution handoff constraints:

## Notes
- Start with 2-3 roles and expand only when unresolved risk remains.
