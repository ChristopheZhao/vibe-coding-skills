# Regression Cases

## Positive Cases
- A new sprint exists but later review would be generic because done signals and negative cases are missing.
- A user asks what exactly a work slice should close before implementation begins.
- A checkpoint owner needs explicit evidence expectations but should not invent them ad hoc.

## Negative Cases
- A request to decide whether work should be one-shot or sprint-required.
- A request to mark a plan `testing` or `completed`.
- A request to emit a checkpoint verdict after validation already ran.

## Boundary Cases
- The sprint is still conceptually unclear.
  - Expected result: do not trigger; upstream mode selection or discussion is still missing.
- The output starts becoming a low-level implementation checklist.
  - Expected result: reject and collapse back to semantic contract fields.
- The contract contains no negative cases.
  - Expected result: fail quality bar; the slice is underspecified.
