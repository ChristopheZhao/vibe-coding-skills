# vibe-coding-skills

Reusable skills for vibe coding agents, with a strict repository layout and deterministic release tooling.

## Repository Layout

```text
vibe-coding-skills/
  .devtools/
    check-structure.sh
    smoke.sh
    release.sh
    release-all.sh
  skills/
    sdd-plan-maintainer/
      SKILL.md
      agents/
      references/
      scripts/
    layered-project-memory/
      SKILL.md
      agents/
      references/
      scripts/
    experience-capture/
      SKILL.md
      agents/
      references/
      scripts/
    knowledge-refresh/
      SKILL.md
      agents/
      references/
      scripts/
    multi-agent-discussion-advisor/
      SKILL.md
      agents/
      references/
      scripts/
```

## Naming Rules

- Repository name should describe a multi-skill collection (for example: `vibe-coding-skills`).
- `skills/<skill-slug>/` is the canonical source for one skill.
- The `skill-slug` must stay stable once published, because it maps to runtime install folder names.

## Skill Directory Contract

Each `skills/<skill-slug>/` directory must include:

- `SKILL.md`

Optional directories (recommended when needed):

- `references/`
- `scripts/`
- `agents/` (platform-specific adapters such as `openai.yaml`)
- `assets/`

Run structure checks before release:

```bash
./.devtools/check-structure.sh
```

## Validate and Release

Validate one skill:

```bash
./.devtools/smoke.sh --skill-dir skills/sdd-plan-maintainer
./.devtools/smoke.sh --skill-dir skills/layered-project-memory
./.devtools/smoke.sh --skill-dir skills/experience-capture
./.devtools/smoke.sh --skill-dir skills/knowledge-refresh
./.devtools/smoke.sh --skill-dir skills/multi-agent-discussion-advisor
```

Smoke architecture:
- `.devtools/smoke.sh` is a dispatcher only.
- Each skill owns its smoke implementation under `skills/<skill>/scripts/smoke.sh` (or `smoke.py`).

Release one skill to Codex:

```bash
./.devtools/release.sh --tool codex --skill-dir skills/sdd-plan-maintainer
```

Release one skill to Claude Code:

```bash
./.devtools/release.sh --tool claude --skill-dir skills/sdd-plan-maintainer
```

Release one skill to Gemini CLI:

```bash
./.devtools/release.sh --tool gemini --skill-dir skills/sdd-plan-maintainer
```

Release one skill to GitHub Copilot:

```bash
./.devtools/release.sh --tool copilot --skill-dir skills/sdd-plan-maintainer
```

Release all skills:

```bash
./.devtools/release-all.sh --tool codex
./.devtools/release-all.sh --tool claude
./.devtools/release-all.sh --tool gemini
./.devtools/release-all.sh --tool copilot
```

All release operations use a whitelist payload:

- `SKILL.md`
- `agents/**` (if present)
- `references/**` (if present)
- `scripts/**` (if present)
- `assets/**` (if present)

This keeps runtime skill directories clean and free of repository-only files.

## Compatibility Baseline

- Core contract is SKILL-first (`SKILL.md` is the single required artifact).
- Platform adapter files are optional and isolated under `agents/`.
- See `docs/compatibility/skills-matrix.md` for profile-specific paths and constraints.
