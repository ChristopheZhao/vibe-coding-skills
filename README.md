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
```

## Naming Rules

- Repository name should describe a multi-skill collection (for example: `vibe-coding-skills`).
- `skills/<skill-slug>/` is the canonical source for one skill.
- The `skill-slug` must stay stable once published, because it maps to runtime install folder names.

## Skill Directory Contract

Each `skills/<skill-slug>/` directory must include:

- `SKILL.md`
- `agents/`
- `references/`
- `scripts/`

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

Release all skills:

```bash
./.devtools/release-all.sh --tool codex
./.devtools/release-all.sh --tool claude
```

All release operations use a whitelist payload:

- `SKILL.md`
- `agents/**`
- `references/**`
- `scripts/**`

This keeps runtime skill directories clean and free of repository-only files.
