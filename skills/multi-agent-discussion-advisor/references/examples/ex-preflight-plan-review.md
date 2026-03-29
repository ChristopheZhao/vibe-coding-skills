# Example: Preflight Plan Review

## Situation
- A phased implementation plan already exists.
- The user wants a multi-role challenge before execution starts.
- The main question is not how to implement tasks yet, but whether the phase split and owner boundaries are safe.

## Expected Mode
- `preflight-review`

## Typical Role Set
- product/value
- architecture/coherence
- implementation/reliability

## Typical Review Output
- `verdict`: `revise`
- Required revisions:
  - keep acceptance under checkpoint ownership in phase 1
  - defer standalone evaluator extraction until two consumers exist

## Why This Belongs Here
- The work is still discussion-phase advisory.
- It should not mutate lifecycle state or become detailed execution planning.
