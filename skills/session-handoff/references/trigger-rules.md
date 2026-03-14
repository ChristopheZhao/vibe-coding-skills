# Trigger Rules

## Should Trigger
- User asks to整理当前 session before opening a new window for the same unfinished task.
- User asks for a handoff/context-offload summary so the next window can continue directly.
- User asks to summarize what this window has done, what remains, and what the next window should read first.

## Should Not Trigger
- User only wants reusable lessons or an experience card.
- User only wants plan status or milestone updates.
- User only wants long-term project memory capture or resume retrieval.
- User asks for raw transcript export.

## MVP Trigger Policy
- Explicit trigger only.
- No `suggest-once`.
- Trigger assumes the old window is still available and can summarize its own context before the new window starts.
