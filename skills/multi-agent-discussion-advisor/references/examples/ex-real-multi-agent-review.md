# Example: Real Multi-agent Discussion Review (Template)

## Scenario
- User asks for project-level product/architecture/implementation assessment and explicitly requests multi-agent discussion.

## Recommended Pattern
- Pattern: `Triad Trade-off`
- Roles: `product`, `architect`, `backend`

## Delegation Directive
Run 3 explorer sub-agents in parallel with disjoint scope:

1. Product reviewer
```text
You are the product reviewer.
Scope: user-facing flows and feature-closure status only.
Task: assess whether current project capabilities are truly deliverable.
Output:
1) key findings
2) closure gaps
3) top risks
4) file references
```

2. Architecture reviewer
```text
You are the architecture reviewer.
Scope: orchestrator/tool/memory/event architecture coherence only.
Task: assess whether target architecture is the enforced main path.
Output:
1) key findings
2) migration residue
3) architecture risks
4) file references
```

3. Backend reliability reviewer
```text
You are the backend reviewer.
Scope: API contracts, state persistence, task execution reliability only.
Task: identify production-readiness blockers.
Output:
1) contract mismatches
2) reliability blockers
3) priority fixes
4) file references
```

## Synthesis Template
- `agent_results`: one section per agent with evidence.
- `synthesis.consensus`: agreed findings.
- `synthesis.disagreements`: conflicting views.
- `synthesis.final_recommendation`: one converged recommendation.

## Guardrail
- This example is discussion-only.
- Do not convert this flow into implementation task execution.
