# Output Contract

## Output Form
- One Markdown file at `docs/session-handoff/SHO-YYYYMMDD-NNNN.md`

## Required Sections
- `Session ID`
- `Generated At`
- `Offload Reason`
- `Session Goal`
- `Overview`
- `Related Refs`
- `Subtask Snapshots`
- `Avoid Repeat`
- `Next Window Boot`
- `Source of Truth`

## Content Requirements
- `Related Refs` must include repo-relative pointers where possible.
- `Related Refs` should annotate older plan refs as `historical` or `reference-only` when the current session has invalidated them as execution entrypoints.
- `Subtask Snapshots` must support multiple subtasks or branches touched by the same session.
- `Avoid Repeat` must contain 1-3 items only.
- `Next Window Boot` must state both:
  - what to read first
  - what the first action should be
- `Next Window Boot` may include one concise `Before coding` line when the next window should not move straight into coding.
- If that line is present, it must stay pointer-first:
  - name the relevant current plan ref when one exists
  - or say that a plan should be created or refreshed before coding
  - but do not inline plan content or acceptance criteria
- `Next Window Boot` should also state what not to continue by default when an older plan has been invalidated.
- `Source of Truth` must explicitly point back to:
  - repository or Git evidence for code facts
  - `docs/plans/`
  - `docs/memory/`
  - `docs/experience/`
- `Source of Truth` should distinguish lifecycle truth from current diagnostic entrypoints so the pack does not become a second status store.

## Quality Bar
- Useful to the next window without reading the old chat transcript.
- Compact enough that the next window can read it first.
- Pointer-first instead of text-dump-heavy.
