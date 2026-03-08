# Collaboration Patterns

These patterns are reusable templates, not fixed case routes.

## Pattern A: Single-role Deep Dive
- Use when uncertainty is narrow and one discipline dominates the decision.
- Typical role: one lead role plus optional reviewer.
- Output focus: boundary clarification and decision assumptions.

## Pattern B: Paired Validation
- Use when one role proposes and another role validates feasibility or impact.
- Delegation hint: spawn 2 explorer agents with proposer/validator split.
- Typical role pairs:
  - Product + Architect
  - Product + Algorithm
  - Backend + Frontend
- Output focus: assumption checks and feasibility checkpoints.

## Pattern C: Triad Trade-off
- Use when at least three dimensions conflict (for example value, feasibility, and delivery complexity).
- Delegation hint: spawn 3 explorer agents (value, architecture, implementation reliability).
- Typical roles:
  - Product, Architect, Algorithm
  - Architect, Backend, Frontend
- Output focus: trade-off table and recommended compromise path.

## Pattern D: Cross-functional Panel
- Use when high-risk solution changes require broad impact review.
- Delegation hint: spawn 4-5 explorer agents only when triad cannot close uncertainty.
- Typical roles: product, architecture, algorithm, backend, frontend, domain expert (subset by necessity).
- Output focus: decision gates, unresolved risks, and escalation points.

## Selection Guidance
- Start from the lightest pattern that can resolve current uncertainty.
- Escalate pattern complexity only when unresolved risks remain.
