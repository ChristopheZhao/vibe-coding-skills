# Output Contract

Use this output structure for every verification result:

```yaml
claim: <one-sentence statement under verification>
verdict: confirmed | revised | inconclusive
impact_on_decision: <how this changes or confirms next action>
evidence:
  - url: <source link>
    title: <short source title>
    date: <publish/update date if available>
    finding: <1-2 sentence relevant finding>
next_action: <concrete next step>
```

## Field Rules
- `claim` must be explicit and testable.
- `verdict` must match evidence quality.
- `impact_on_decision` should describe concrete coding impact.
- `evidence` should be concise and traceable.
- `next_action` must be executable.
