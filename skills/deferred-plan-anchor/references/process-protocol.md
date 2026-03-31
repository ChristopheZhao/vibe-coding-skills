# Process Protocol

## 1. Confirm the Decision Surface
- Verify this is a deferred technical direction with current planning impact.
- Reject generic backlog, roadmap, or immediate execution requests.

## 2. Capture the Deferred Plan
- Record:
  - long-horizon goal
  - why it is deferred now
  - current deviation from that goal
  - current "do not" guardrails
  - allowed short-term work
  - reopen trigger
- Keep the wording concise and operational.

## 3. Maintain Independent Status
- Use the deferred-plan index under `docs/deferred-plans/DEFERRED_PLAN_INDEX.json`.
- Keep v1 to one `active` deferred plan.
- Move completed or superseded plans out of the active effect surface.

## 4. Derive the Current Summary
- `CURRENT.md` is derived from the unique `active` deferred plan only.
- If there is no active deferred plan, write a clear no-active summary.
- Do not let archived or superseded plans continue influencing the current summary.

## 5. Resolve for Planning
- The host workflow may call `resolve-for-planning` with scope, topic, and plan-kind hints.
- Resolve whether:
  - the deferred-plan system is enabled
  - a unique active plan exists
  - the active plan is stale
  - the active plan applies to the requested planning context
- Return current guardrails only when all conditions pass.

## 6. Respect the Execution Boundary
- Do not create or mutate `docs/plans/` artifacts.
- Do not block planning automatically.
- Supply guardrails; let the host or planning owner decide how to use them.
