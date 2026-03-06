# Process Protocol

## 1. Activation Check
- Activate only for continuity, handoff, repeated-attempt mitigation, or focused memory retrieval.
- Skip for one-off tiny edits and pure Q and A.

## 2. Boundary Enforcement
- Git remains source of truth for code facts.
- SDD remains source of truth for plan lifecycle when SDD is used.
- Memory stores only `why/tried/learned/next` plus anchors.
- Use pointer-first storage: prefer links/refs over duplicated long text.

## 3. Runtime Storage
Use `memory_ops.py init` to ensure:
- `docs/memory/MEMORY_INDEX.json`
- `docs/memory/state/current.json`
- `docs/memory/events/events.jsonl`
- `docs/memory/insights/`
- `docs/memory/snapshots/`

## 4. Capture Flow
1. Record key event with `capture` and required anchors.
2. Include insight fields when the node has diagnostic or decision depth.
3. Attach pointers (`evidence`, `doc_ref`) instead of copying full logs/docs.
4. Use `plan_id` when SDD plan exists; otherwise use `topic_id`.
5. Let score-based promotion run automatically, or call `promote` explicitly.

## 5. Retrieval Flow
1. Select profile: `resume`, `debug`, or `release`.
2. Retrieve ranked events and linked insights.
3. If no strong signal exists, use fallback pack from L1 + recent L2.

## 6. Consistency Governance
Run `doctor`:
- after milestone transitions
- before handoff
- when schema or record quality is in doubt

## 7. Retention Governance
- Run `gc` periodically to prune low-value records.
- Keep enough key events and snapshots for continuity.
- Apply `--dry-run` before aggressive retention changes.

## 8. Command Examples
```bash
python scripts/memory_ops.py init --root .

python scripts/memory_ops.py capture --root . \
  --topic-id checkout-timeout \
  --event-type blocker \
  --summary "integration test failed on API contract mismatch" \
  --problem-key api-contract-mismatch \
  --result failed \
  --impact high \
  --next-action "align response schema and rerun tests" \
  --doc-ref docs/adr/0012-retry-policy.md#decision \
  --evidence logs/test-api-contract.txt

python scripts/memory_ops.py retrieve --root . --profile debug --topic-id checkout-timeout
python scripts/memory_ops.py doctor --root .
python scripts/memory_ops.py gc --root . --retain-events 200 --retain-key-events 100 --retain-snapshots 50 --dry-run
```
