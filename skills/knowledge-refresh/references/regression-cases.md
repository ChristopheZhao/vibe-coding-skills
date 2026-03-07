# Regression Cases

## Trigger Cases
- User explicitly asks for source-backed verification of a technical claim.
- User asks for latest official behavior before selecting implementation path.
- Same technical point is disputed and current context lacks strong evidence.

## Non-Trigger Cases
- Local compile/test error investigation where repository evidence is available.
- One-off tiny edits unrelated to external factual correctness.
- Experience summarization requests that belong to `experience-capture`.
- Project continuity retrieval requests that belong to `layered-project-memory`.

## Guard Rails
- Do not auto-trigger on every uncertainty phrase.
- Do not replace normal coding verification (read code, run tests) when local evidence is enough.
- Keep report concise and actionable; avoid long transcript-style dumps.
