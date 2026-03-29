# Output Contract

## Required Fields
- `task_frame`: goal, scope, constraints, unknowns
- `mode_verdict`: one of:
  - `one-shot`
  - `research-first`
  - `discussion-first`
  - `sprint-required`
- `why_not_alternatives`: why the main rejected alternatives are weaker
- `risk_factors`: explicit risk signals behind the verdict
- `next_owner`: the next skill or workflow owner

## Conditional Fields
- `coarse_sprints`: required only for `sprint-required`
- `discussion_focus`: required only for `discussion-first`
- `research_targets`: required only for `research-first`

## Coarse Sprint Fields
- `title`
- `what_this_closes`
- `why_this_boundary_exists`

## JSON Shape (Reference)
```json
{
  "task_frame": {
    "goal": "Add harness-aware skill selection before implementation starts",
    "scope": ["new skill contract", "phase-1 rollout guidance"],
    "constraints": ["no second lifecycle owner"],
    "unknowns": ["whether acceptance should be standalone or profile-first"]
  },
  "mode_verdict": "sprint-required",
  "why_not_alternatives": {
    "one-shot": "Would mix contract design, owner-boundary changes, and review-surface evolution in one rollout",
    "discussion-first": "High-level direction is already aligned; the missing piece is staged execution"
  },
  "risk_factors": [
    "cross-skill boundary changes",
    "late validation risk",
    "owner overlap if shipped continuously"
  ],
  "coarse_sprints": [
    {
      "title": "Standalone skill contracts",
      "what_this_closes": "New top-level contracts for execution mode and contract design",
      "why_this_boundary_exists": "These contracts must stabilize before extensions consume them"
    },
    {
      "title": "Existing owner extensions",
      "what_this_closes": "Preflight and acceptance semantics under existing owners",
      "why_this_boundary_exists": "Owner boundaries must be validated after the new contracts exist"
    }
  ],
  "next_owner": "sdd-plan-maintainer"
}
```
