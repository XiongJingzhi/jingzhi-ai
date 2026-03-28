# Role Prompt Index

Use the following role prompt files as the role-specific instructions for spawned agents.

Each role MUST be loaded from its own file. Do not inline multiple roles into one prompt source.

## Professional Committee Roles

- `roles/family-cfo.md`
- `roles/family-chief-allocation-officer.md`
- `roles/family-risk-officer.md`
- `roles/macro-scenario-analyst.md`
- `roles/execution-strategist.md`

## Summary Role

- `roles/munger-synthesis-chair.md`

## Loading Rule

- Always load exactly 5 professional role agents:
  - `family-cfo`
  - `family-chief-allocation-officer`
  - `family-risk-officer`
  - `macro-scenario-analyst`
  - `execution-strategist`
- Then load 1 summary agent:
  - `munger-synthesis-chair`

## Coordination Rule

- Before any professional role starts evaluating, the summary agent must assemble one shared research packet and send the same packet to all 5 professional roles.
- The 5 professional roles produce independent first-round outputs.
- The summary agent reads all first-round outputs and produces the final synthesis.
- If the user keeps asking about an unresolved conflict, reopen discussion only with the relevant professional roles plus the summary agent.
