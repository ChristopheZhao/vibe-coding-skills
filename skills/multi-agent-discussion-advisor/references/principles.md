# Discussion Advisor Principles

## 1. Discussion-only Boundary
- This skill is for pre-execution discussion quality.
- It must not produce runtime dispatch or execution-order commands.
- Allowed: delegate coding sub-agents for analysis discussion.
- Not allowed: orchestrate business execution flow.

## 2. Principle + Example Dual Track
- Abstract principles define constraints and quality bar.
- Examples calibrate style and reasoning patterns.
- Examples are references, not hardcoded trigger rules.

## 3. Signal-driven Activation
- Trigger by uncertainty, disagreement, cross-role dependency, or blocked path.
- Avoid fixed-case matching as the primary trigger method.

## 4. Minimal Sufficient Roles
- Add roles only when they resolve a concrete uncertainty or risk.
- Avoid role inflation that increases coordination overhead with no decision gain.

## 5. Real Multi-agent over Role-play
- When the user explicitly asks for multi-agent discussion, run real sub-agents.
- Do not replace explicit multi-agent requests with single-model role simulation.

## 6. Explainable Recommendation
- Every role and pattern recommendation must include explicit rationale.
- Avoid opaque recommendations without traceable reason.

## 7. Low Disturbance
- Prioritize discussion milestones; avoid high-frequency interruptions.
- If the user is already executing tasks, do not hijack the flow.

## 8. Clean Handoff
- Output should include a concise handoff note for execution-phase skills.
- Handoff note should contain constraints and checkpoints, not runtime scheduling details.
