# Process Protocol

## Step 1: Problem Frame
- Clarify objective, constraints, unknowns, and decision deadline.
- Classify whether the mode is `standard-discussion` or `preflight-review`.
- Output: `context_frame`.

## Step 2: Collaboration Necessity Check
- Determine whether single-role analysis is enough.
- If not enough, identify missing perspectives.
- Output: `collaboration_need`.

## Step 2A: Preflight Review Focus (Optional)
- Only for `preflight-review` mode.
- Review plan assumptions, scope boundary, owner boundary, and evaluator readiness.
- Output: `preflight_review`.

## Step 3: Pattern and Role Selection
- Match the signal profile to a collaboration pattern.
- Select the minimal sufficient role set.
- For each role, record what uncertainty it resolves.
- Output: `recommended_pattern`, `role_set`, and `role_rationale`.

## Step 4: Real Sub-agent Delegation
- Create launch-signal package with concrete sub-agent scopes and expected output schema.
- Keep scopes disjoint and evidence-oriented.
- Follow `references/subagent-protocol.md` for explicit delegation directive.
- Output: `agent_plan` and `launch_signal`.

## Step 5: Findings Aggregation
- Collect each sub-agent output (after host coding agent executes the launch signal).
- Summarize consensus points and disagreements.
- Output: `agent_results` and `synthesis`.

## Step 6: Discussion Checkpoints
- Define checkpoints that must be confirmed before execution.
- Output: `risk_checkpoints`.

## Step 7: Handoff Note
- Summarize what execution-phase planning should preserve.
- Output: `handoff_note`.

## Exit Rule
- If user asks for execution breakdown or task scheduling, stop this protocol and switch to execution-planning skill.
