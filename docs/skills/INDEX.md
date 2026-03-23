English | [简体中文](INDEX.zh-CN.md)

# Skill Catalog

This catalog provides the public entry point for the skills shipped in this repository.
For each skill, the source of truth is the linked `skills/<slug>/SKILL.md`.

| Skill | Primary Value | Typical Output | When to Use | Boundary Note | Read |
| --- | --- | --- | --- | --- | --- |
| `sdd-plan-maintainer` | Make complex coding work executable and governable | concrete plan + lifecycle status updates | when users ask for concrete feature/fix planning, progress tracking, or plan closure | owns plan lifecycle, not runtime orchestration | [SKILL.md](../../skills/sdd-plan-maintainer/SKILL.md) |
| `checkpoint-gatekeeper` | Prevent unverified checkpoint output from leaking forward | checkpoint checklist + gate verdict artifacts | when phase-based work must validate the current checkpoint before advancing, with bounded auto-remediation and explicit escalation | owns checkpoint verification artifacts, not plan lifecycle state | [SKILL.md](../../skills/checkpoint-gatekeeper/SKILL.md) |
| `checkpoint-commit-advisor` | Decide whether and how to freeze a dirty worktree before the next phase starts | checkpoint commit strategy advisory | when a large or mixed dirty tree may need governance-anchor or known-bad snapshot commits before a new phase, new plan, or new window | owns checkpoint commit strategy advice, not lifecycle truth or git history execution | [SKILL.md](../../skills/checkpoint-commit-advisor/SKILL.md) |
| `session-handoff` | Offload current-session context for next-window continuation | session continuation pack | when the current window should summarize progress, blockers, and next steps before continuing the same task in a new window | owns session-level aggregation, not plan/memory/experience truth | [SKILL.md](../../skills/session-handoff/SKILL.md) |
| `layered-project-memory` | Preserve project continuity across interrupted work | layered memory records + focused context packs | when users need durable project state, key events, repeated-attempt memory, or resume/debug/release context | owns continuity memory, not experience-card persistence | [SKILL.md](../../skills/layered-project-memory/SKILL.md) |
| `experience-capture` | Convert hard-earned lessons into reusable guidance | experience cards | when users ask to summarize reusable lessons, decision rules, or review checklists | owns cross-task lessons, not next-window handoff | [SKILL.md](../../skills/experience-capture/SKILL.md) |
| `knowledge-refresh` | Reduce stale assumptions with external evidence | source-backed claim verdict | when a technical claim needs verification, official freshness, or stronger evidence before coding decisions | uses authoritative external sources, not local-only debugging | [SKILL.md](../../skills/knowledge-refresh/SKILL.md) |
| `multi-agent-discussion-advisor` | Improve discussion quality before execution starts | discussion advisory card + launch specification | when high-uncertainty product/requirement/architecture discussion needs real multi-role synthesis | advisory-only; not direct implementation or runtime orchestration | [SKILL.md](../../skills/multi-agent-discussion-advisor/SKILL.md) |

## Notes

- This page is a public catalog, not the semantic source of truth.
- Detailed workflow, triggers, and non-goals remain in each linked `SKILL.md`.
- Repository structure and cross-tool packaging rules remain documented in [README.md](../../README.md) and [docs/compatibility/skills-matrix.md](../compatibility/skills-matrix.md).
