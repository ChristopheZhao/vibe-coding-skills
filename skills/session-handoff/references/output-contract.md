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
- `Subtask Snapshots` must support multiple subtasks or branches touched by the same session.
- `Avoid Repeat` must contain 1-3 items only.
- `Next Window Boot` must state both:
  - what to read first
  - what the first action should be
- `Source of Truth` must explicitly point back to:
  - `docs/plans/`
  - `docs/memory/`
  - `docs/experience/`

## Quality Bar
- Useful to the next window without reading the old chat transcript.
- Compact enough that the next window can read it first.
- Pointer-first instead of text-dump-heavy.
