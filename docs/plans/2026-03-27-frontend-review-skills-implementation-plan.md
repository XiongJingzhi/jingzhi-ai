# Frontend Review Skills Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a reusable frontend review skill system with one runner, three critics, one judge, and shared review references that let a coding agent iterate on UI until both score and quality gates pass.

**Architecture:** The implementation creates five skills under `skills/` plus one shared reference package. The runner is responsible for evidence gathering and orchestration, each critic owns a specific review domain, and the judge merges critic outputs into a final verdict with dual stop gates.

**Tech Stack:** Markdown skill files, shared reference documents, existing repo `skills/` conventions, agent-oriented prompt contracts.

---

### Task 1: Verify repository layout and target paths

**Files:**
- Verify: `skills/`
- Verify: `docs/plans/2026-03-27-frontend-review-skills-design.md`

**Step 1: Confirm the target directories exist**

Run: `ls skills docs/plans`
Expected: both directories exist

**Step 2: Check for conflicting skill names**

Run: `rg --files skills | rg 'frontend-(review-runner|ui-critic|qa-critic|a11y-perf-critic|review-judge|review-shared)'`
Expected: no matches for a fresh implementation

**Step 3: Commit**

```bash
git add docs/plans/2026-03-27-frontend-review-skills-design.md docs/plans/2026-03-27-frontend-review-skills-implementation-plan.md
git commit -m "docs: add frontend review skills design and plan"
```

### Task 2: Create the shared reference package

**Files:**
- Create: `skills/frontend-review-shared/references/UI_REVIEW_RUBRIC.md`
- Create: `skills/frontend-review-shared/references/QA_REVIEW_RUBRIC.md`
- Create: `skills/frontend-review-shared/references/A11Y_PERF_RUBRIC.md`
- Create: `skills/frontend-review-shared/references/PAGE_TYPE_RULES.md`
- Create: `skills/frontend-review-shared/references/ANTI_PATTERNS.md`
- Create: `skills/frontend-review-shared/references/REVIEW_OUTPUT_SCHEMA.md`
- Create: `skills/frontend-review-shared/references/REVIEW_LOOP_POLICY.md`
- Create: `skills/frontend-review-shared/references/PAGE_REVIEW_TASK_TEMPLATE.md`

**Step 1: Write the shared rubric files**

Write concise reference files that define:
- scoring priorities
- blocker rules
- page-type-specific emphasis
- output keys and required sections
- loop stopping rules

**Step 2: Review for duplication**

Run: `wc -l skills/frontend-review-shared/references/*.md`
Expected: each file stays focused and reasonably small

**Step 3: Commit**

```bash
git add skills/frontend-review-shared/references
git commit -m "feat: add shared references for frontend review skills"
```

### Task 3: Create the review runner skill

**Files:**
- Create: `skills/frontend-review-runner/SKILL.md`

**Step 1: Write the frontmatter**

Include:
- `name: frontend-review-runner`
- a description that clearly triggers when a coding agent needs to collect browser evidence and orchestrate a frontend review loop

**Step 2: Define the runner workflow**

Document:
- required inputs
- browser tool contract
- evidence collection order
- failure and degraded-evidence behavior
- invocation order for critics and judge
- final output packet expected by the main agent

**Step 3: Verify the skill stays orchestration-focused**

Check that the runner:
- does not score the page itself
- does not rewrite code
- does not duplicate critic rubric details

**Step 4: Commit**

```bash
git add skills/frontend-review-runner/SKILL.md
git commit -m "feat: add frontend review runner skill"
```

### Task 4: Create the UI critic skill

**Files:**
- Create: `skills/frontend-ui-critic/SKILL.md`

**Step 1: Write the frontmatter**

Include:
- `name: frontend-ui-critic`
- a trigger description for structure, hierarchy, layout, and visual review

**Step 2: Define review process**

Cover:
- page type inference
- goal inference
- dimension scoring
- blocker handling
- evidence-first review
- follow-language-of-user rule

**Step 3: Link shared references**

Explicitly point to:
- `skills/frontend-review-shared/references/UI_REVIEW_RUBRIC.md`
- `skills/frontend-review-shared/references/PAGE_TYPE_RULES.md`
- `skills/frontend-review-shared/references/ANTI_PATTERNS.md`
- `skills/frontend-review-shared/references/REVIEW_OUTPUT_SCHEMA.md`

**Step 4: Commit**

```bash
git add skills/frontend-ui-critic/SKILL.md
git commit -m "feat: add frontend UI critic skill"
```

### Task 5: Create the QA critic skill

**Files:**
- Create: `skills/frontend-qa-critic/SKILL.md`

**Step 1: Write the frontmatter**

Include:
- `name: frontend-qa-critic`
- a trigger description for primary flow, states, errors, validation, and interaction review

**Step 2: Define review process**

Cover:
- default flow checks
- primary action checks
- loading, empty, error, and success states
- console and network behavior relevance
- blocker handling

**Step 3: Link shared references**

Explicitly point to:
- `skills/frontend-review-shared/references/QA_REVIEW_RUBRIC.md`
- `skills/frontend-review-shared/references/ANTI_PATTERNS.md`
- `skills/frontend-review-shared/references/REVIEW_OUTPUT_SCHEMA.md`

**Step 4: Commit**

```bash
git add skills/frontend-qa-critic/SKILL.md
git commit -m "feat: add frontend QA critic skill"
```

### Task 6: Create the accessibility and performance critic skill

**Files:**
- Create: `skills/frontend-a11y-perf-critic/SKILL.md`

**Step 1: Write the frontmatter**

Include:
- `name: frontend-a11y-perf-critic`
- a trigger description for accessibility, semantics, keyboard reachability, and runtime health review

**Step 2: Define review process**

Cover:
- accessibility checks
- performance hygiene checks
- degraded behavior when Lighthouse or a11y tools are absent
- blocker handling for critical accessibility failures

**Step 3: Link shared references**

Explicitly point to:
- `skills/frontend-review-shared/references/A11Y_PERF_RUBRIC.md`
- `skills/frontend-review-shared/references/REVIEW_OUTPUT_SCHEMA.md`
- `skills/frontend-review-shared/references/REVIEW_LOOP_POLICY.md`

**Step 4: Commit**

```bash
git add skills/frontend-a11y-perf-critic/SKILL.md
git commit -m "feat: add frontend accessibility and performance critic skill"
```

### Task 7: Create the final judge skill

**Files:**
- Create: `skills/frontend-review-judge/SKILL.md`

**Step 1: Write the frontmatter**

Include:
- `name: frontend-review-judge`
- a trigger description for merging multiple critic reports into a final review verdict

**Step 2: Define the merge contract**

Cover:
- how to merge overlapping findings
- how to handle disagreements
- how to preserve blockers
- how to calculate final score
- how to evaluate score and quality gates
- how to decide continue vs stop

**Step 3: Link shared references**

Explicitly point to:
- `skills/frontend-review-shared/references/REVIEW_OUTPUT_SCHEMA.md`
- `skills/frontend-review-shared/references/REVIEW_LOOP_POLICY.md`
- `skills/frontend-review-shared/references/ANTI_PATTERNS.md`

**Step 4: Commit**

```bash
git add skills/frontend-review-judge/SKILL.md
git commit -m "feat: add frontend review judge skill"
```

### Task 8: Validate trigger coverage and consistency

**Files:**
- Review: `skills/frontend-review-runner/SKILL.md`
- Review: `skills/frontend-ui-critic/SKILL.md`
- Review: `skills/frontend-qa-critic/SKILL.md`
- Review: `skills/frontend-a11y-perf-critic/SKILL.md`
- Review: `skills/frontend-review-judge/SKILL.md`

**Step 1: Check naming and descriptions**

Run: `for f in skills/frontend-*/SKILL.md; do echo "== $f =="; sed -n '1,20p' "$f"; done`
Expected: each file has valid frontmatter with clear trigger descriptions

**Step 2: Check reference links**

Run: `rg 'frontend-review-shared/references' skills/frontend-*/SKILL.md`
Expected: each critic and judge references only the files it needs

**Step 3: Check that responsibilities do not blur**

Review manually for:
- runner does orchestration
- critics do domain review
- judge does merge and stop logic

**Step 4: Commit**

```bash
git add skills/frontend-*/SKILL.md
git commit -m "chore: validate frontend review skill contracts"
```

### Task 9: Dry-run the review loop contract

**Files:**
- Review: `skills/frontend-review-runner/SKILL.md`
- Review: `skills/frontend-review-judge/SKILL.md`
- Review: `skills/frontend-review-shared/references/PAGE_REVIEW_TASK_TEMPLATE.md`

**Step 1: Create a sample review packet mentally or in notes**

Use a hypothetical page input with:
- page goal
- URL
- screenshots
- logs
- one blocker
- one near-pass score

**Step 2: Verify the contract answers these questions**

The documents should make it obvious:
- what evidence is required
- how missing evidence is handled
- how blockers are escalated
- how stop conditions work
- what the main agent should change next

**Step 3: Commit**

```bash
git add skills/frontend-review-runner/SKILL.md skills/frontend-review-judge/SKILL.md skills/frontend-review-shared/references/PAGE_REVIEW_TASK_TEMPLATE.md
git commit -m "docs: finalize frontend review loop contract"
```

### Task 10: Final verification

**Files:**
- Verify: `skills/frontend-review-runner/SKILL.md`
- Verify: `skills/frontend-ui-critic/SKILL.md`
- Verify: `skills/frontend-qa-critic/SKILL.md`
- Verify: `skills/frontend-a11y-perf-critic/SKILL.md`
- Verify: `skills/frontend-review-judge/SKILL.md`
- Verify: `skills/frontend-review-shared/references/*.md`

**Step 1: Run repository checks**

Run: `find skills/frontend-review-* -maxdepth 3 -type f | sort`
Expected: all intended files are present

**Step 2: Inspect git status**

Run: `git status --short`
Expected: only intended new skill and doc files are changed

**Step 3: Sanity read the top of each file**

Run: `for f in $(find skills/frontend-review-* -name '*.md' | sort); do echo "== $f =="; sed -n '1,40p' "$f"; done`
Expected: no malformed frontmatter, no obvious copy-paste mistakes

**Step 4: Commit**

```bash
git add skills/frontend-review-* docs/plans/2026-03-27-frontend-review-skills-*.md
git commit -m "feat: add frontend review skill suite"
```
