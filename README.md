English | [简体中文](README.zh-CN.md)

<table>
  <tr>
    <td valign="middle">
      <h1>vibe-coding-skills</h1>
      <p>Reusable, production-oriented skills for vibe coding workflows.</p>
    </td>
    <td align="right" valign="middle" width="220">
      <img src="docs/assets/vibe-coding-skills-logo.png" alt="vibe-coding-skills logo" width="180" />
    </td>
  </tr>
</table>

This repository focuses on high-value guidance that improves coding outcomes:
- planning and lifecycle governance
- project memory continuity
- reusable experience capture
- external knowledge verification
- multi-agent discussion setup

License: [MIT](LICENSE)

## What This Repository Provides

- A SKILL-first repository contract (`skills/<slug>/SKILL.md` is required).
- Deterministic validation and release tooling under `.devtools/`.
- Cross-tool packaging profiles for `codex`, `claude`, `cursor`, `gemini`, and `copilot`.
- A growing skill library for real vibe coding scenarios.

## Current Skills (v1)

![vibe-coding-skills current skills overview](docs/assets/vibe-coding-skills-banner.png)

| Skill | Primary Value | Typical Output | Key Characteristics |
| --- | --- | --- | --- |
| `sdd-plan-maintainer` | Make complex coding work executable and governable | concrete plan + lifecycle status updates | module decomposition, milestone tracking, completion gates, plan archive/index sync |
| `layered-project-memory` | Keep project continuity across interrupted sessions | layered memory records + focused context packs | L1/L2/L3 memory model, Git anchors, pointer-first evidence, summary derived from records |
| `experience-capture` | Convert hard alignment/problem-solving moments into reusable knowledge | experience cards | decision rules, anti-patterns, review checklist, explicit boundary from project memory |
| `knowledge-refresh` | Reduce stale assumptions with external verification | evidence-based claim verdict (`confirmed/revised/inconclusive`) | source priority, freshness-aware checks, authoritative reference-first workflow |
| `multi-agent-discussion-advisor` | Improve discussion quality before execution starts | discussion advisory card + sub-agent launch briefs | minimal-sufficient role design, launch specification for host coding agent, advisory-only boundary |

## Repository Contract

Each skill lives in `skills/<skill-slug>/`.

Required:
- `SKILL.md`

Optional (recommended when needed):
- `references/`
- `scripts/`
- `agents/` (tool/provider adapters such as `openai.yaml`)
- `assets/`

The `skill-slug` should stay stable after publishing because runtime installers map folder names directly.

Example (single-skill structure):

```text
skills/example-skill/
  SKILL.md
  references/
  scripts/
  agents/
  assets/
```

## Prerequisites

Required:
- `bash`
- `python3`
- `rsync`

Python package:
- `PyYAML` (used by smoke frontmatter validation)

Recommended Python environment management:

```bash
uv venv
source .venv/bin/activate
uv pip install pyyaml
```

Fallback without `uv`:

```bash
python3 -m pip install pyyaml
```

## Validate

Repository structure check:

```bash
./.devtools/check-structure.sh
```

Validate one skill:

```bash
./.devtools/smoke.sh --skill-dir skills/sdd-plan-maintainer
```

Smoke design:
- `.devtools/smoke.sh` is a dispatcher.
- Each skill owns its own smoke entry under `skills/<skill>/scripts/smoke.sh` (or `smoke.py`).

## Release

Default behavior:
- `release.sh` and `release-all.sh` target `user-level` skill directories unless an explicit runtime path is provided.

Release one skill:

```bash
./.devtools/release.sh --tool codex   --skill-dir skills/sdd-plan-maintainer
./.devtools/release.sh --tool claude  --skill-dir skills/sdd-plan-maintainer
./.devtools/release.sh --tool cursor  --skill-dir skills/sdd-plan-maintainer
./.devtools/release.sh --tool gemini  --skill-dir skills/sdd-plan-maintainer
./.devtools/release.sh --tool copilot --skill-dir skills/sdd-plan-maintainer
```

Release all skills:

```bash
./.devtools/release-all.sh --tool codex
./.devtools/release-all.sh --tool claude
./.devtools/release-all.sh --tool cursor
./.devtools/release-all.sh --tool gemini
./.devtools/release-all.sh --tool copilot
```

Release to a project-level directory by overriding the runtime path:

```bash
./.devtools/release.sh --tool copilot --skill-dir skills/experience-capture --runtime-root /path/to/project/.github/skills/experience-capture
./.devtools/release.sh --tool cursor  --skill-dir skills/experience-capture --runtime-root /path/to/project/.cursor/skills/experience-capture
```

All release operations use a whitelist payload:
- `SKILL.md`
- `agents/**` (if present)
- `references/**` (if present)
- `scripts/**` (if present)
- `assets/**` (if present)

This keeps runtime skill directories clean and avoids shipping repository-only files.

## Compatibility Baseline

- Core contract is SKILL-first (`SKILL.md` is the required source of truth).
- Platform adapter files are optional and isolated under `agents/`.
- See `docs/compatibility/skills-matrix.md` for profile paths and adapter constraints.

## Verified Platforms

Validated in real use:
- `Codex`
- `Claude Code`
- `Gemini CLI`
- `GitHub Copilot`
- `Cursor`

Verified install/load paths:
- `Codex`: personal-level runtime release via `~/.codex/skills/<skill>`
- `Claude Code`: personal-level runtime release via `~/.claude/skills/<skill>`
- `Gemini CLI`: personal-level runtime release via `~/.gemini/skills/<skill>`
- `GitHub Copilot`: project-level `.github/skills/<skill>` and personal-level `~/.copilot/skills/<skill>`
- `Cursor`: project-level `.cursor/skills/<skill>`, project-level `.agents/skills/<skill>`, and personal-level `~/.cursor/skills/<skill>`

Practical note:
- These skills are built around a SKILL-first, tool-agnostic repository contract.
- Even when a platform uses a different discovery path, the reusable source asset remains `skills/<skill>/SKILL.md` plus optional `references/`, `scripts/`, `agents/`, and `assets/`.

## Milestones and Roadmap

Current milestone:
- v1 foundation shipped with 5 skills for core vibe coding scenarios.

Next expansion focus:
- Long-running workflow skills: support resumable execution guidance, checkpoint/handoff discipline, and low-loss context continuity for multi-session coding work.
- CI-related skills: support test strategy selection, release gate checks, regression triage guidance, and CI-friendly quality workflows.
- Release/install strategy refinement: add clearer project-level vs user-level publishing support and platform-specific install guidance where needed.

Roadmap principle:
- New skills should stay guidance-first (prior knowledge + workflow patterns + reusable scripts), not business runtime orchestration modules.
