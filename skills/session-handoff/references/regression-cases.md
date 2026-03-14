# Trigger-Boundary Regression Cases

## Should Trigger
1. User asks to整理当前 session so a new window can continue the same unfinished refactor.
2. User asks for a handoff/context-offload summary before opening a new window.
3. Current session touched multiple subtasks and the user wants one continuation pack for next-window continuation.

## Should Not Trigger
1. User only asks for reusable lessons or an experience card.
2. User only asks to update plan status or execution checklist.
3. User only asks for long-term memory capture or resume retrieval.
4. User asks for raw transcript export.

## Boundary Assertions
- The pack must be produced in the old window, not after the new window starts.
- The pack must not replace plan, memory, or experience truth.
- The pack may reference related docs, but must not depend on a specific skill name being present.
- MVP must stay explicit-trigger only.
