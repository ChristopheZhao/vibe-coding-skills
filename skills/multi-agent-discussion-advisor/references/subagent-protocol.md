# Sub-agent Delegation Protocol

Use this protocol when the skill triggers and multi-role synthesis is required.
Goal: define a launch signal package so the host coding agent can run real multi-agent analysis, then synthesize one decision recommendation.

## 1. Pre-delegation Inputs
- `decision_goal`: what must be decided.
- `scope`: repository/path/module scope.
- `constraints`: timeline, quality bar, cost, compatibility, compliance.
- `evidence_requirement`: file references, API contracts, tests, or docs that must be cited.

## 2. Pattern -> Agent Set Mapping

### Pattern B: Paired Validation
- Agent count: 2
- Suggested roles:
  - proposer-reviewer
  - feasibility-reviewer

### Pattern C: Triad Trade-off
- Agent count: 3
- Suggested roles:
  - product/value
  - architecture/coherence
  - implementation/reliability

### Pattern D: Cross-functional Panel
- Agent count: 4-5 (only when risk is high)
- Suggested roles:
  - product
  - architecture
  - backend/runtime
  - frontend/contract
  - domain/compliance (optional)

## 3. Host-Agent Launch Directive
When this skill triggers with `multi-role-recommended`, the host coding agent should run this sequence:

1. Select minimal sufficient roles from uncertainty map.
2. Spawn one `explorer` sub-agent per role in parallel.
3. Use disjoint scope per agent (no duplicated ownership).
4. Wait for results and synthesize consensus/disagreements.

Note:
- Explicit user ask for multi-agent review is highest-priority trigger.
- User does not need to provide a full role list; roles are inferred by this skill.

Per-agent creation brief template:
```text
You are the <role> reviewer.
Scope: <explicit module/path boundaries>.
Task: evaluate <decision_goal> under <constraints>.
Required output:
1) key findings (3-5)
2) top risks (max 3)
3) recommendation
4) concrete file references
Do not propose runtime execution orchestration.
```

## 3.1 Launch Signal Package (Required)
Output a structured package for the host coding agent:
- `agent_count`
- `roles`
- `agent_briefs` (one brief per role)
- `success_criteria`
- `synthesis_rule`

## 4. Mandatory Synthesis
- Produce `agent_results` with one entry per delegated agent.
- Produce `synthesis.consensus`, `synthesis.disagreements`, and `synthesis.final_recommendation`.
- If agent outputs conflict and evidence is weak, set verdict `inconclusive`.

## 5. Guardrails
- Multi-agent delegation is for analysis discussion only.
- Do not delegate direct implementation tasks in this skill.
- If user switches to execution planning, hand off to `sdd-plan-maintainer`.
- This skill provides launch specification; host coding agent executes the actual sub-agent creation.
