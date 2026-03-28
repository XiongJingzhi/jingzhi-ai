# Frontend Review Skills Design

**Date:** 2026-03-27

## Goal

Create a reusable frontend review skill system for coding agents. The system should let a main agent dispatch a review-oriented subagent, collect real page evidence from a running app, score the page across multiple dimensions, and convert the review into concrete code-change tasks. The loop should continue until both score and quality gates pass.

## Scope

This design covers:
- a browser-driven review runner
- three specialized critics
- one final judge
- shared rubrics, anti-patterns, and IO schemas
- stopping conditions for iterative code improvement

This design does not cover:
- standalone QA platform UX
- hosted review dashboards
- visual diff infrastructure
- automatic code rewriting without a main agent

## User Workflow

The intended workflow is:

1. The main coding agent builds or updates a frontend page.
2. The main agent dispatches a review subagent using the review runner skill.
3. The runner opens the page with browser tools, captures evidence, and normalizes the review input.
4. The runner invokes three critics:
   - UI critic
   - QA critic
   - a11y/perf critic
5. The runner invokes the judge to merge results and compute pass/fail gates.
6. The judge returns a structured review packet with score, blockers, top fixes, and a task list for the main agent.
7. The main agent edits code and reruns the review loop until both stop conditions pass.

## System Components

### 1. `frontend-review-runner`

Role:
- orchestrates the review cycle
- opens the page and captures evidence
- prepares a shared review packet
- invokes critics and judge in sequence

Responsibilities:
- verify the page is reachable
- collect desktop and mobile screenshots
- collect DOM snapshot
- collect console logs
- collect network summary
- collect accessibility summary
- collect Lighthouse summary if supported
- mark missing evidence explicitly
- pass the evidence package into the critics and judge

The runner is not a scorer. It is an evidence collector and orchestrator.

### 2. `frontend-ui-critic`

Role:
- evaluates structure, hierarchy, clarity, layout logic, visual consistency, and page-type fit

Primary question:
- does the page clearly support its intended user goal

Dimensions owned:
- structure clarity
- information hierarchy
- interaction comprehensibility
- visual consistency
- responsive adaptation

### 3. `frontend-qa-critic`

Role:
- evaluates task completion quality and realistic interaction reliability

Primary question:
- can the user finish the primary flow without confusion or breakdowns

Dimensions owned:
- interaction comprehensibility
- state completeness
- primary flow integrity
- error handling and recovery
- form validation and submission reliability
- console and network issues that affect behavior

### 4. `frontend-a11y-perf-critic`

Role:
- evaluates access, semantics, keyboard support, readability, and basic runtime health

Primary question:
- is the page accessible and technically healthy enough to trust

Dimensions owned:
- accessibility
- engineering and performance hygiene
- responsive issues tied to usability
- severe semantic or contrast failures

### 5. `frontend-review-judge`

Role:
- merges critic reports into a final verdict
- resolves overlap and scoring conflicts
- decides whether another coding iteration is required

Primary outputs:
- final score
- pass/fail judgment
- blocker list
- score gate result
- quality gate result
- continue/stop decision
- prioritized fixes
- repair task sheet for the main agent

## Page Types

The system is generic and should support page-type-aware scoring. Supported page types:
- landing
- dashboard
- form
- settings
- detail
- list
- auth
- onboarding
- unknown

If the page type is not provided, critics infer the most likely page type from the evidence and mark that inference explicitly.

## Evidence Contract

The review system must prefer real page evidence over source-only reasoning.

Expected evidence:
- page URL
- desktop screenshot
- mobile screenshot
- DOM snapshot
- current state description
- console logs
- network summary
- accessibility report
- Lighthouse summary

Evidence policy:
- if evidence exists, use it
- if evidence is missing, mark the related conclusion as lower confidence
- if the runner cannot access a browser tool, report degraded review coverage instead of pretending the page was fully reviewed

## Browser Tool Contract

Browser access should be treated as a runtime capability, not as a separate scoring skill.

The review runner and critics should assume these tools may be available:
- `browser`
- `screenshot`
- `dom_inspector`
- `console`
- `network`
- `lighthouse`
- `accessibility`

Expected behavior:
- the runner uses these tools to gather evidence
- critics consume the evidence and may request follow-up interaction checks when needed
- if any tool is unavailable, the runner marks the gap in the evidence packet and the judge lowers confidence accordingly

## Scoring Model

Default total score: 100

Shared dimensions:
- structure clarity: 25
- information hierarchy: 20
- interaction comprehensibility: 15
- visual consistency: 15
- state completeness: 10
- responsive adaptation: 5
- accessibility: 5
- engineering and performance hygiene: 5

Not every critic scores every dimension independently. Each critic owns a subset, and the judge produces the final merged score.

## Blockers

Any of the following must be treated as a blocker:
- above-the-fold page goal is unclear
- primary action is missing or hard to identify
- fatal console errors affect core functionality
- a core region is unusable
- mobile layout is severely broken
- form submission cannot complete
- the page violates explicit product principles in a severe way
- core actions are not keyboard reachable

If a blocker exists:
- the final result is `not passed`
- the quality gate fails
- the stop decision must be `continue_iteration`

## Stop Conditions

The review loop uses two independent gates.

### Score Gate

Default:
- final score must be `>= 85`

This threshold should be configurable per task.

### Quality Gate

All conditions must pass:
- no blockers
- structure clarity `>= 18/25`
- information hierarchy `>= 14/20`
- interaction comprehensibility `>= 10/15`
- state completeness `>= 6/10`
- responsive adaptation `>= 3/5`
- accessibility `>= 3/5`
- engineering and performance hygiene `>= 3/5`

### Final Stop Rule

Stop only when:
- `score_gate_passed = true`
- `quality_gate_passed = true`

Otherwise:
- `should_continue_iteration = true`

## Output Contract

All critic outputs should be structured and consistent enough for the judge to merge them.

Each critic should output:
- page goal judgment
- page type judgment
- domain score or dimension scores
- observations
- major issues
- evidence
- explicit inferences
- blockers
- top fixes
- a repair task list for the main agent

The judge should output:
- final page goal judgment
- final score
- pass/fail conclusion
- blocker summary
- dimension-level merged scores
- scoring rationale
- score gate result
- quality gate result
- continue/stop decision
- top five fixes
- final task sheet for the main agent

## Language Policy

The review output should follow the language of the current user conversation unless the task explicitly requires another language.

## File Layout

Recommended layout:

```text
skills/
  frontend-review-runner/
    SKILL.md
  frontend-ui-critic/
    SKILL.md
  frontend-qa-critic/
    SKILL.md
  frontend-a11y-perf-critic/
    SKILL.md
  frontend-review-judge/
    SKILL.md
  frontend-review-shared/
    references/
      UI_REVIEW_RUBRIC.md
      QA_REVIEW_RUBRIC.md
      A11Y_PERF_RUBRIC.md
      PAGE_TYPE_RULES.md
      ANTI_PATTERNS.md
      REVIEW_OUTPUT_SCHEMA.md
      REVIEW_LOOP_POLICY.md
      PAGE_REVIEW_TASK_TEMPLATE.md
```

## Design Principles

- real evidence over source-only guessing
- major issues over cosmetic nitpicks
- repeatable scoring over stylistic eloquence
- task-driving output over commentary
- generic framework with page-type-specific rules
- stop only when both score and quality gates pass

## Open Implementation Decisions

Implementation should still decide:
- how the runner receives the local dev URL
- whether critics operate only on prepared evidence or may perform follow-up checks
- whether to store example prompts or sample review packets under references
- whether to include `agents/openai.yaml` metadata for discoverability in the first version
