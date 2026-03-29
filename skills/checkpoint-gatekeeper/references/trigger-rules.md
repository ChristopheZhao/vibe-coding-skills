# Trigger Rules

## Should Trigger
1. User says the next phase must not start until the current checkpoint is verified.
2. The current task is explicitly split into checkpoints or stages.
3. A complex refactor needs bounded auto-remediation and a clear stop signal when validation fails.
4. The user wants a stage or final acceptance check that should stay under the existing checkpoint owner.

## Should Not Trigger
1. User only asks for plan creation or lifecycle status updates.
2. The task is a one-shot bugfix with no phase boundary.
3. The work needs a continuous long-running orchestrator more than a checkpoint gate.

## Guardrails
- Trigger on phase or checkpoint gating needs, not on every test run.
- The skill should complement plans, not replace them.
- Use a clear `plan_id` + `checkpoint` pair whenever possible.
- Treat `acceptance` as a profile under checkpoint ownership, not as a new verdict owner.
