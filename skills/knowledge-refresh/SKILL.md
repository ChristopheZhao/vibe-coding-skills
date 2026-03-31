---
name: knowledge-refresh
description: Validate uncertain or time-sensitive technical claims with authoritative external sources. Use when users ask for verification, latest official guidance, or stronger evidence for disputed technical points. Do not use for local code debugging, test-only verification, or experience/memory capture.
---

# Knowledge Refresh

## Purpose
Use this skill to reduce wrong decisions caused by stale prior knowledge or weak evidence.
This skill provides a lightweight workflow for deciding when to verify externally, where to search first, and how to report evidence clearly.

## Activation Cues
Activate when any condition is true:
- User explicitly asks to verify, provide sources, or check latest official guidance.
- The claim depends on external and time-sensitive facts (version behavior, policy, standard, pricing, release notes).
- The same technical point is disputed across multiple rounds and current evidence is weak.

Do not activate when any condition is true:
- Local code, logs, or tests can directly verify the issue.
- The task is deterministic logic with no external-fact dependency.
- The request is mainly about project memory continuity or reusable experience-card capture.

## Scope Limit
This skill does:
- external evidence-oriented verification guidance
- source selection and freshness-aware search workflow
- verdict reporting with evidence pointers

This skill does not:
- replace runtime orchestrator logic
- implement trigger scoring engines
- persist project state memory
- persist reusable experience cards

## Ownership Boundary
- `layered-project-memory` owns project continuity memory (`state/events/insights`).
- `experience-capture` owns reusable cross-task experience cards.
- `knowledge-refresh` owns external claim verification guidance.

Boundary rule:
- This skill may output evidence pointers and recommendations, but does not write memory/experience records by itself.

## Script Decision
Use the skill-bundled `scripts/smoke.sh` for structure/contract checks only.
No business runtime script is required in v1.

## Workflow Contract
1. Define one explicit `claim` that needs verification.
2. Select source priority and freshness window.
3. Search and collect minimal authoritative evidence set.
4. Compare evidence against current assumption.
5. Output structured verdict: `confirmed`, `revised`, or `inconclusive`, with impact on next action.

## Hard Rules
- Prefer first-party authoritative sources before secondary summaries.
- Include publish/update date when available.
- Never present an unverified statement as confirmed fact.
- If evidence conflicts or is insufficient, return `inconclusive`.
- Keep trigger logic cue-based and explainable; do not add in-skill scoring engines.

## Resource Map
- Read `references/positioning-boundary.md` for scope and boundary details.
- Read `references/activation-cues.md` for activation and non-activation cues.
- Read `references/source-priority.md` for source ranking and trust policy.
- Read `references/search-playbook.md` for search and comparison process.
- Read `references/output-contract.md` for output structure and field definitions.
- Read `references/examples.md` for positive and negative examples.
- Read `references/regression-cases.md` for trigger-boundary regression cases.
- Use the skill-bundled `scripts/smoke.sh` for deterministic smoke checks.
