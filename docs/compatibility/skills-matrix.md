# Skills Compatibility Matrix

## 1. Repository Baseline

- Required: `skills/<skill>/SKILL.md`
- Optional: `references/`, `scripts/`, `agents/`, `assets/`
- Core trigger semantics should live in `SKILL.md` frontmatter (`name`, `description`).
- `agents/*` is adapter-only, not source-of-truth for skill semantics.

## 2. Tool Profile Mapping (This Repository)

| Tool Profile | Default Runtime Path | Core Artifact | Adapter Notes |
| --- | --- | --- | --- |
| `codex` | `~/.codex/skills/<skill>` | `SKILL.md` | `agents/openai.yaml` optional |
| `claude` | `~/.claude/skills/<skill>` | `SKILL.md` | Keep Anthropic-specific config separate from OpenAI adapter |
| `gemini` | `~/.gemini/skills/<skill>` | `SKILL.md` | Keep Gemini-specific conventions outside `openai.yaml` |
| `copilot` | `~/.copilot/skills/<skill>` | `SKILL.md` | Prefer repo-level portability; avoid OpenAI-only assumptions |
| `cursor` | `~/.cursor/skills/<skill>` | `SKILL.md` | Cursor-specific rules/modes should be treated as adapter layer |

## 3. Design Rules

1. Do not make `agents/openai.yaml` a hard dependency for generic smoke/structure checks.
2. Keep platform-specific invocation policy in adapter files only.
3. Keep skill business boundary and workflow in `SKILL.md` + `references/`.
4. Prefer scripts under `scripts/` for deterministic behavior across tool profiles.
