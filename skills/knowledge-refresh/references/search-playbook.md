# Search Playbook

## Step-by-Step
1. Freeze the target claim in one sentence.
2. Identify impact level: will this claim change implementation or architecture decisions.
3. Pick source class using `source-priority.md`.
4. Query authoritative sources first; widen scope only if needed.
5. Normalize versions and time windows before comparing alternatives.
6. Collect minimal evidence set (links + date/version + key finding).
7. Compare evidence to the current assumption.
8. Produce verdict and next action.

## Query Framing Tips
- Include product name, feature name, and version/time hints.
- Add `official`, `docs`, `release notes`, or standard identifier keywords.
- For papers/standards, search by canonical title or document number.
- For model-vs-model comparison, require same comparison window or annotate mismatch explicitly.

## Stop Conditions
- Evidence is sufficient to confirm or revise the claim.
- Evidence is conflicting with no clear resolution; mark `inconclusive`.
- Additional search will not materially change current decision.
