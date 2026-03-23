# Example: Two-Layer Checkpoint

- Situation: a large dirty tree mixes `docs/plans/`, `docs/session-handoff/`, and implementation files before a major refactor begins.
- Recommendation:
  - `decision`: `commit_now`
  - `strategy`: `two-layer`
  - Layer 1: `governance_anchor`
  - Layer 2: `implementation_snapshot`
- Why:
  - freeze the current plan and handoff truth separately from the known-bad code snapshot
  - reduce later diff noise when the new refactor starts
