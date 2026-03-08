# Platform Adapters (Discussion Phase)

This file describes discussion-phase adaptation hints only.
It is not a runtime dispatch specification.

## Codex
- Use discussion guidance to decide whether sub-agent collaboration is worth the overhead.
- When user explicitly asks for multi-agent discussion, execute the skill-provided `launch_signal` with real `spawn_agent` delegation for analysis scopes.
- Keep output as advisory card; do not dispatch business runtime workflows.
- If user asks to execute implementation, hand off to execution-planning flow.

## Claude Code
- Use the same trigger principles and output contract.
- Use the skill-provided launch specification and execute real subagent task delegation for discussion analysis when explicitly requested.
- Keep recommendation content model-agnostic: pattern + role rationale + checkpoints.
- Do not turn this skill into a hidden business runtime orchestration layer.

## Cross-platform Rule
- Maintain one semantic source of truth in `SKILL.md` and references.
- Adapter files should adjust phrasing and interface hints only.
