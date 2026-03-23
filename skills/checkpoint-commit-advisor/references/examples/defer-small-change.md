# Example: Defer for a Small Dirty Tree

- Situation: one or two obvious code edits in a single file family with no plan or handoff transition.
- Recommendation:
  - `decision`: `defer`
  - `strategy`: `null`
- Why:
  - the dirty tree is already small and clear
  - a checkpoint strategy discussion would add process noise rather than clarity
