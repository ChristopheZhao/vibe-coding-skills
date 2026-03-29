# Contract Fields

## `what`
Describe the semantic closure for this slice.
This should say what capability, boundary cleanup, or risk reduction the slice closes.

## `why`
Explain why this boundary exists.
Typical reasons:
- stabilize a new contract before extensions consume it
- isolate owner-boundary risk
- validate one semantic closure before the next stage starts

## `done signals`
State the observable facts that later owners can check.
These should be task-specific, not generic phrases like "works correctly".

## `evidence checklist`
List the concrete artifacts that later review or checkpoint flows should inspect.
Examples:
- file paths
- smoke results
- regression test names
- design docs or examples

## `negative cases`
Name the important failure modes that should not remain true when the slice is done.

## `suggested checkpoints`
Suggest later checkpoint names or evaluation surfaces, but do not emit verdicts.
