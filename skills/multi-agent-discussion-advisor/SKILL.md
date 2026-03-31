---
name: multi-agent-discussion-advisor
description: "Guide discussion-phase multi-agent decision making for vibe coding projects by providing role design and a launch specification for the host coding agent to start multi-agent review. Use when users need cross-role synthesis to evaluate options and converge on one recommendation across product, requirement, architecture, or hard-problem discussions, including preflight plan review before execution starts. Do not use for execution planning, business runtime orchestration, or direct implementation."
---

# Multi-Agent Discussion Advisor

## Purpose
Use this skill to design discussion roles and emit a launch signal package before execution starts.
The output must include:
- a role design for current scenario (who should participate and why)
- role-level goals (what each agent must prove or challenge)
- explicit sub-agent creation briefs (ready for host-agent tool-triggered delegation)
- synthesis contract for consolidating actual sub-agent findings

## Activation Cues
Activate when any condition is true:
- High-uncertainty discussion needs cross-role synthesis to converge on one方案, even if user does not specify exact roles.
- User asks whether multiple roles/agents are needed for requirement or architecture discussion.
- User asks to assess current project product capabilities and technical architecture design from multiple roles.
- User explicitly asks: "评估下当前项目的产品功能，技术架构设计方案" / "需要多角色综合分析确定方案" / "多角色讨论后定方案".
- User explicitly asks to run real multi-agent review (for example: "开多个agent评审" / "用多agent讨论后给结论").
- A draft plan or sprint structure exists and the user wants a preflight review before execution starts.
- The same design point is repeatedly disputed and needs cross-role alignment.
- A proposed solution path is blocked and the team needs reframing suggestions.
- User explicitly asks for collaboration strategy guidance in discussion phase.

Do not activate when any condition is true:
- The request is already execution planning, task breakdown, or milestone tracking.
- The request is direct coding implementation or runtime scheduling.
- The issue can be closed by a local test/log check without cross-role discussion.

## Scope Limit
This skill does:
- discussion-phase collaboration pattern guidance
- role design and launch-signal design for discussion analysis
- preflight plan review guidance before execution starts
- minimal-sufficient role selection guidance
- risk-checkpoint and handoff-note guidance

This skill does not:
- replace runtime orchestrator logic in the target business system
- generate or execute business runtime dispatch commands
- own sub-agent scheduling; host coding agent owns actual sub-agent launch
- replace SDD execution planning or plan lifecycle governance
- persist project memory or reusable experience cards by itself

## Ownership Boundary
- `sdd-plan-maintainer` owns execution planning and lifecycle governance.
- `layered-project-memory` owns project continuity memory.
- `experience-capture` owns reusable cross-task experience cards.
- `multi-agent-discussion-advisor` owns discussion-phase collaboration guidance.

Boundary rule:
- This skill defines how sub-agents should be launched for analysis-only discussion work.
- The host coding agent executes the actual multi-agent launch using its tool surface.
- If user request shifts to execution planning, route to `sdd-plan-maintainer`.

## Script Decision
Use the skill-bundled `scripts/smoke.sh` for structure and contract checks only.
No business runtime script is required in v1.

## Workflow Contract
1. Frame the discussion problem: goal, constraints, uncertainties.
2. If the mode is `preflight`, review plan assumptions, owner boundaries, and evaluator readiness before execution starts.
3. Design a scenario-fit role set and role-level goals.
4. Produce explicit sub-agent creation briefs and launch signal package from the role design.
5. Hand off launch signal package to host coding agent for actual sub-agent launch (use `references/subagent-protocol.md`).
6. Collect sub-agent findings (if launched), identify consensus and disagreements.
7. Produce advisory card with evidence, risk checkpoints, and handoff note.
8. If user asks to execute implementation, stop this skill flow and hand off to execution planning skill.

## Hard Rules
- Advisory only: no business runtime orchestration commands.
- Examples are references, not exhaustive case limits.
- Keep trigger logic cue-based and explainable; do not add in-skill scoring engines.
- Prefer minimal sufficient roles over role inflation.
- Do not write memory/experience records unless user explicitly asks and target skill is invoked.
- Triggered flow must include role design + role goals + explicit sub-agent creation briefs.
- User is not required to provide a full role list; the skill must infer minimal sufficient roles from uncertainty signals.
- If user explicitly asks for real multi-agent discussion, do not answer with role-play-only output; provide launch signal package for host-agent to start at least 2 sub-agents unless tooling is unavailable.
- Each delegated sub-agent brief must have a concrete scope and required output format.
- In `preflight` mode, the skill may emit `approve`, `revise`, or `block` review guidance, but it must not mutate plan lifecycle state.

## Resource Map
- Read `references/principles.md` for abstract design principles.
- Read `references/trigger-signals.md` for trigger and non-trigger signals.
- Read `references/process-protocol.md` for discussion workflow protocol.
- Read `references/collaboration-patterns.md` for reusable collaboration patterns.
- Read `references/subagent-protocol.md` for delegation protocol and synthesis rules.
- Read `references/role-selection.md` for minimal sufficient role selection.
- Read `references/output-contract.md` for advisory-card output schema.
- Read `references/platform-adapters.md` for Codex/Claude discussion-phase adapter hints.
- Read `references/regression-cases.md` for trigger-boundary regression cases.
- Read `references/examples/README.md` for example index and usage notes.
- Use the skill-bundled `scripts/smoke.sh` for deterministic smoke checks.
