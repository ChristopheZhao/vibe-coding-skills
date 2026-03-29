# Output Contract

## 1. Required Fields
- `context_frame`: objective, constraints, unknowns.
- `collaboration_need`: why multi-role discussion is needed (or not).
- `recommended_pattern`: selected collaboration pattern and rationale.
- `role_set`: minimal sufficient roles.
- `role_rationale`: role -> uncertainty mapping.
- `agent_plan`: delegated sub-agent scopes and expected outputs.
- `launch_signal`: host-agent executable multi-agent launch specification.
- `agent_results`: summarized findings from real sub-agents.
- `synthesis`: consensus, disagreement, and final recommendation.
- `risk_checkpoints`: discussion checkpoints before execution.
- `handoff_note`: concise input for execution-phase planning.

## 2. Optional Fields
- `discussion_mode`: `standard-discussion` or `preflight-review`
- `preflight_review`: plan-level advisory fields for `approve`, `revise`, or `block`
- `alternatives_considered`: rejected patterns and reasons.
- `decision_confidence`: low/medium/high with reason.
- `open_questions`: unresolved issues that block execution.
- `assessment_dimensions`: project-level evaluation dimensions (for example product capability coverage, architecture coherence, implementation risk).
- `agent_trace_refs`: optional references to sub-agent messages/runs.

## 3. Verdict Enum
- `single-role-ok`
- `multi-role-recommended`
- `inconclusive`

## 4. JSON Shape (Reference)
```json
{
  "verdict": "multi-role-recommended",
  "context_frame": {
    "goal": "Define AI product PRD scope and feasibility boundaries",
    "constraints": ["MVP in 4 weeks", "existing inference budget"],
    "unknowns": ["online latency tolerance", "model quality baseline"]
  },
  "collaboration_need": "Feasibility and product value are both uncertain",
  "recommended_pattern": "Triad Trade-off",
  "role_set": ["product", "algorithm", "architect"],
  "role_rationale": {
    "product": "clarify user value and acceptance boundary",
    "algorithm": "evaluate capability and quality-risk",
    "architect": "evaluate system impact and delivery risk"
  },
  "agent_plan": [
    {
      "role": "product",
      "scope": "assess user-facing capability completeness and closure gaps",
      "expected_output": "feature-closure findings with top risks"
    },
    {
      "role": "architect",
      "scope": "assess architecture coherence and migration residue",
      "expected_output": "architecture-risk findings and evidence"
    }
  ],
  "launch_signal": {
    "agent_count": 2,
    "roles": ["product", "architect"],
    "success_criteria": [
      "each agent returns evidence-backed findings",
      "synthesis includes consensus and disagreements"
    ],
    "synthesis_rule": "merge on evidence consistency, else mark inconclusive"
  },
  "agent_results": [
    {
      "role": "product",
      "summary": "Core flow is visible but export/share are not full backend closures"
    },
    {
      "role": "architect",
      "summary": "Target modules exist but not yet the single enforced main path"
    }
  ],
  "discussion_mode": "preflight-review",
  "preflight_review": {
    "verdict": "revise",
    "focus": [
      "owner boundary remains unclear between acceptance and checkpoint ownership"
    ],
    "required_revisions": [
      "keep acceptance under checkpoint owner for phase 1",
      "defer standalone evaluator skill extraction"
    ]
  },
  "synthesis": {
    "consensus": [
      "Current project is a strong prototype with migration residue"
    ],
    "disagreements": [
      "Whether to expand features now or harden runtime first"
    ],
    "final_recommendation": "Stabilize contracts and state persistence before feature expansion"
  },
  "risk_checkpoints": [
    "MVP acceptance metric agreed",
    "model capability baseline validated",
    "critical dependency risk acknowledged"
  ],
  "handoff_note": "Execution planning must preserve MVP boundary and model-quality gate."
}
```
