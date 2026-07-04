# AI-Assisted E2E Test Automation — How It Works

> **The QA Engineer is the architect and reviewer. AI is the executor.**
>
> The QA Engineer defines what needs to be built and whether the result is acceptable.
> AI reads the codebase, proposes designs, writes code, runs tests, and traces failures.
> Nothing is written or committed without the QA Engineer's approval.

This project uses Claude Code with a set of slash commands and specialized agents to cover the full test engineering lifecycle — from reviewing requirements to maintaining the suite over time.

---

## Roles

### QA Engineer — Architect & Reviewer

The QA Engineer makes every meaningful decision:

- **What** to test and why
- **Whether** a design is correct before any code is written
- **Whether** a plan makes sense before implementation starts
- **Whether** to accept a fix or override it
- **What** gets committed and merged
- **Which** failures are worth investigating vs. acceptable to skip
- **When** a test suite is healthy enough to ship
- **What** counts as a quality gate pass or fail
- **How** to prioritize scenarios (P1 / P2 / P3)
- **Whether** optimization suggestions are worth acting on

The QA Engineer also:

- Writes the requirement or user story that starts the workflow
- Answers clarifying questions raised by AI during requirements review
- Describes app changes that trigger maintenance
- Reads reports and decides the next action
- Overrides any AI decision at any stage

The QA Engineer never needs to write boilerplate, hunt for selectors, trace call stacks, or parse raw test output.

### AI — Executor

AI handles all the execution work:

- Reads the codebase and maps existing patterns
- Proposes page object structure, locators, and test scenarios
- Writes code that follows the project's conventions exactly
- Runs tests, reads output, and classifies failures to a specific file and line
- Updates broken tests when the app changes

AI never makes architectural decisions, never commits without approval, and never skips a quality gate.

---

## How a Stage Works

```
QA Engineer runs a command
      ↓
Command breaks the work into steps
      ↓
Agents execute each step (read, write, run, analyze)
      ↓
QA Engineer reviews the output and approves or rejects
      ↓
Move to the next stage
```

---

## Lifecycle Overview

| # | Stage | Engineer | AI |
|---|-------|----------|----|
| 0 | Requirements Review | writes the requirement, answers clarifying questions | checks testability, flags ambiguities, asks questions |
| 1 | Test Plan | approves or rejects scope, scenarios, and priorities | defines what to test: scope, scenarios, risks, coverage goals |
| 2 | Explore Codebase | triggers exploration, defines scope | reads files, maps structure, finds reusable patterns |
| 3 | Design | approves or rejects page object + test case design | proposes locators, methods, test scenarios |
| 4 | Implement | approves plan before code is written | writes page object, fixtures, test file |
| 5 | Debug | runs tests, decides whether to apply fixes | reads output, traces root cause, classifies failures |
| 6 | Apply Fixes | approves which fixes to apply | applies fixes per classification, reruns tests |
| 7 | Review | review, final approval | checks POM/AAA/FIRST compliance, flags issues |
| 8 | Commit & PR | approves commit message and PR description | stages files, writes message, opens PR |
| 9 | CI Execution | monitors pipeline | reads CI output, diagnoses env-specific failures |
| 10 | Reporting | reads report, decides next action | parses output, summarizes pass/fail/flaky/gaps |
| 11 | Maintenance | describes what changed in the app | traces broken tests, updates selectors/methods |
| 12 | Optimization | decides what to keep or drop | detects flaky/slow tests, flags redundant coverage |

**Key pattern:**
- **Engineer owns:** intent (requirements, approvals, decisions)
- **AI owns:** execution (reading, writing, running, analyzing)
- **Shared:** design and review — AI proposes/checks, Engineer approves/decides

---

## Full Command Sequence

### Manual (step-by-step, full control)

```
/requirements_review <slug> <requirement>    ← Is this testable?
/test_plan <slug>                            ← What to test and why?
/explore_codebase                            ← What already exists?
/design_tests <slug> <description>           ← Plan the page object + tests
/implement_tests <slug>                      ← Write the code
/run_tests <scope>                           ← Run the suite
/debug                                       ← Classify failures
/apply_fixes <scope>                         ← Apply diagnosed fixes
/review <scope>                              ← Final POM/AAA/FIRST check
/open_pr                                     ← Stage files, write message, open PR
/ci [<pr-number>]                            ← Monitor pipeline, diagnose failures
/reporting <scope>                           ← Summary report
```

### Autonomous (hands-off, stages 0–6 in one command)

```
/autorun <slug> <requirement>                ← Run everything end-to-end
/review <scope>                              ← Final manual check
/open_pr                                     ← Commit and open PR
```

For ongoing work (no new tests):

```
/maintenance <app> <what changed>            ← App changed, fix broken tests
/optimization <scope>                        ← Suite health check
/reporting <scope>                           ← Report results
```

---

## Commands

### `/autorun <slug> <requirement>`

**Stages:** 0–6 — autonomous end-to-end pipeline

**When to use:** You have a requirement and want working, passing tests with minimal involvement.

**What happens:**
1. Runs requirements review — resolves ambiguities using best judgment (documents assumptions)
2. Produces a test plan
3. Explores the codebase (3 parallel agents)
4. Designs the page object and test cases
5. Implements code phase by phase — auto-retries review/fix cycles (max 3 per phase)
6. Runs the full suite — auto-debugs and fixes failures (max 2 cycles)
7. Reports final results

**Stops automatically if:**
- Requirement is `NOT TESTABLE`
- Design cannot be completed after 2 attempts
- A phase cannot be reviewed/fixed after 3 cycles
- A failure cannot be diagnosed with `MEDIUM` or `HIGH` confidence
- Tests still fail after 2 debug/fix cycles

**Output:** Code files in `pages/` and `tests/` + `thoughts/reports/YYYY-MM-DD-<slug>.md`

> After `/autorun` completes, run `/review <scope>` for a final manual check, then `/open_pr`.

---

### `/requirements_review <slug> <requirement>`

**Stage:** 0 — Requirements Review

**When to use:** Before writing a single test. Paste the ticket, user story, or plain description.

**What happens:**
1. Checks if the requirement is testable — is the outcome observable?
2. Flags ambiguous words ("valid", "correct", "should work")
3. Identifies missing edge cases
4. Asks clarifying questions

**Output:** `thoughts/requirements/YYYY-MM-DD-<slug>.md`

**Verdict:** `READY` / `NEEDS CLARIFICATION` / `NOT TESTABLE`

Only proceed to `/test_plan` when the verdict is `READY`.

---

### `/test_plan <slug>`

**Stage:** 1 — Test Plan

**When to use:** After requirements are confirmed `READY`.

**What happens:**
1. Defines the scope: which pages, flows, and scenarios to cover
2. Lists specific test scenarios with priority (P1 / P2 / P3)
3. Identifies risks and coverage goals
4. Flags missing edge cases or out-of-scope items

**Output:** `thoughts/test-plans/YYYY-MM-DD-<slug>.md`

> ⚠️ The QA Engineer must approve the plan before moving to `/explore_codebase`.

---

### `/explore_codebase`

**Stage:** 2 — Explore Codebase

**When to use:** After the test plan is approved, to map existing patterns before designing.

**What happens:**
1. Reads all page objects, base classes, fixtures, test files
2. Maps structure: class hierarchy, method patterns, locator conventions
3. Identifies reusable components

**Output:** `thoughts/research/YYYY-MM-DD-<topic>.md`

This runs automatically inside `/design_tests` too — run it separately only to explore without designing.

---

### `/design_tests <slug> <description>`

**Stage:** 3 — Design

**When to use:** After the test plan is approved.

**What happens:**
1. Explores the codebase to understand existing patterns
2. Proposes a **page object design** — class name, locators, method signatures
3. Proposes **test cases** — each with AAA breakdown (Arrange / Act / Assert)
4. Waits for QA Engineer approval at each step before continuing

**Output:** `thoughts/test-designs/YYYY-MM-DD-<slug>.md` + `.claude/agents/design.md`

> ⚠️ Nothing is written to code until the QA Engineer approves the design.

---

### `/implement_tests <slug>`

**Stage:** 4 — Implement

**When to use:** After the design from `/design_tests` has been approved.

**Prerequisite:** A design document must exist in `thoughts/test-designs/` for the given slug.

**What happens:**
1. Checks that `thoughts/test-designs/YYYY-MM-DD-<slug>.md` exists — stops if not
2. Generates a phased plan (shows the phases, asks for confirmation)
3. For each phase:
   - Writes code: locators → page object → fixture → test file
   - Runs automated review (naming, POM, AAA, Playwright rules)
   - Runs Code Quality Checks
   - Only moves to next phase when current phase passes all checks

**Output:** Code files in `pages/` and `tests/`

> ⚠️ Each phase requires review + test pass before proceeding. Failures are shown to the QA Engineer, who decides how to handle them.

---

### `/run_tests <scope>`

**Stage:** 5 — Run Tests

**When to use:** After `/implement_tests` completes, or any time you need to run the suite manually.

Scope can be:
- App name: `acceptapayment`
- Test file: `tests/accept_a_payment/test_card.py`
- Marker: `smoke`
- Node ID: `tests/accept_a_payment/test_card.py::TestPageLoadAndInitialState::test_page_title_is_card`

**What happens:**
1. Runs pytest for the given scope
2. Saves raw output to `thoughts/runs/`
3. If all pass → suggests `/reporting`
4. If failures → shows output and suggests `/debug`

**Output:** `thoughts/runs/YYYY-MM-DD-<scope-slug>.txt`

---

### `/debug [<output>]`

**Stage:** 6 — Debug

**When to use:** After `/run_tests` produces failures. If called with no argument, automatically reads all known output locations: `thoughts/runs/`, `test-logs/`, `test-results/failed_tests/`, `report.html`, `allure-results/`.

**What happens:**
1. Collects and aggregates failures from all available output sources (de-duplicated by test node ID)
2. If no failures found → done
3. If failures → spawns a `bug-tracer` for each unique failing test
4. Each failure is classified: `SELECTOR` / `TIMING` / `LOGIC` / `FIXTURE` / `ASSERTION` / `IMPORT` / `CONFIG` / `FLAKY` / `ENVIRONMENT`
5. Reports exact file + line + what needs to change

**Output:** `thoughts/debug/YYYY-MM-DD-<slug>.md`

---

### `/apply_fixes <scope>`

**Stage:** 7 — Apply Fixes

**When to use:** After `/debug` produces a diagnosis and the QA Engineer approves applying the fixes.

Scope matches what was passed to `/debug`.

**What happens:**
1. Reads the debug report from `thoughts/debug/`
2. For each diagnosed failure, delegates the fix to the `implement` agent by classification
3. Reruns the affected tests after each fix to confirm it passes
4. Reports which fixes were applied and whether any failures remain

**Output:** Updated files in `pages/` and/or `tests/`; rerun results confirm pass or surface remaining failures

> ⚠️ The QA Engineer decides which fixes to apply — AI never applies fixes without approval.

---

### `/review <scope>`

**Stage:** 7 — Review

**When to use:** After implementation passes tests, before committing — to verify code quality against project standards.

Scope can be:
- App name: `acceptapayment`
- Test file: `tests/accept_a_payment/test_card.py`
- Feature slug: `card`
- Omit to review all files changed since last commit

**What happens:**
1. Identifies files to review (from argument or `git diff`)
2. Spawns a `review` agent to check: POM structure, AAA pattern, FIRST principles, Playwright patterns, naming conventions, Allure decorators, locator quality
3. Presents issues grouped by severity (HIGH / MEDIUM / LOW)
4. Asks whether to fix automatically or manually

**Output:** Review result with `file:line` references for every issue

> ⚠️ HIGH severity issues must be resolved before `/open_pr`.

---

### `/open_pr`

**Stage:** 8 — Commit & PR

**When to use:** After `/review` approves the code and all tests pass.

**What happens:**
1. Shows changed files and asks for confirmation to stage them
2. Drafts a commit message based on the changes and repo style — waits for QA Engineer approval
3. Stages files and commits with the approved message
4. Drafts a PR title and description — waits for QA Engineer approval
5. Pushes the branch and opens the PR

**Output:** PR URL

> ⚠️ Nothing is committed or pushed without explicit approval of both the commit message and PR description.

---

### `/ci [<pr-number>]`

**Stage:** 8 — CI Execution

> ⚠️ Full CI automation is pending MCP integration. Current usage requires manual monitoring.

**When to use:** After pushing a branch or opening a PR, to monitor the pipeline and diagnose failures.

**What happens:**
1. Fetches the CI run status for the current branch or given PR
2. If jobs failed, downloads the full log for each failing job
3. Classifies each failure: `ENVIRONMENT` / `IMPORT` / `CONFIG` / `SELECTOR` / `TIMING` / `TEST_LOGIC` / `FLAKY`
4. Recommends fixes based on classification
5. Applies config-level fixes if approved; delegates test-level fixes to `implement` agent

**Output:** `thoughts/debug/YYYY-MM-DD-ci-<slug>.md`

---

### `/reporting <scope>`

**Stage:** 9 — Reporting

**When to use:** After running tests when a structured summary is needed. Scope: `all`, app name, or marker.

**What happens:**
1. Runs the full test suite for the scope
2. Calculates pass rate, slowest tests, flaky signals
3. Identifies coverage gaps (untested pages, missing negative tests)

**Output:** `thoughts/reports/YYYY-MM-DD-<scope>.md`

---

### `/maintenance <app> <description of what changed>`

**Stage:** 10 — Maintenance

**When to use:** The web app changed and tests broke or need updating.

Examples:
```
/maintenance acceptapayment "pay button text changed from Pay now to Submit payment"
```

**What happens:**
1. Explores the codebase to find everything that references the changed element
2. Shows the QA Engineer the proposed changes before touching any file
3. Updates locator constants and page object methods
4. Runs the affected tests to confirm they pass
5. Does NOT change what a test asserts — only how it gets there

**Output:** `thoughts/maintenance/YYYY-MM-DD-<slug>.md`

---

### `/optimization <scope>`

**Stage:** 11 — Optimization

**When to use:** Periodically, or when the suite feels slow or unreliable. Scope: `all`, app name, or `quick` (static analysis only).

**What happens:**
1. Runs the suite with timing data
2. Flags: flaky patterns, slow tests (>10s), duplicate coverage, dead methods/locators, missing edge cases
3. Groups findings by priority: High (reliability) → Medium (speed) → Low (cleanup)
4. Asks the QA Engineer which issues to fix

**Output:** `thoughts/optimization/YYYY-MM-DD-<scope>.md`

---

## Agents

Agents are the specialists that commands delegate to. The QA Engineer never calls agents directly — commands call them. Each agent has a narrow responsibility and strict rules about what it can and cannot do.

### `requirements-reviewer`
Checks testability of requirements. Flags ambiguous language. Asks clarifying questions. Produces a verdict. **Cannot write code.**

### `codebase-explorer`
Reads files, maps structure, identifies patterns and reusable components. Every claim must cite a `file:line`. **Cannot suggest improvements or write code.**

### `test-planner`
Defines what to test: scope, scenarios, priorities, risks, and coverage goals. Works from reviewed requirements and codebase exploration. **Cannot design page objects or write code.**

### `design`
Produces the architectural specification: file paths, class names, locators, method signatures, data flow. **Cannot write Python code — only specs.**

### `plan`
Converts the design into a phased implementation plan with acceptance criteria per phase. **Cannot write code.**

### `implement`
The only agent that writes Python code. Follows the plan and design exactly. Works one phase at a time. Stops and escalates if anything is unclear.

### `review`
Runs through a strict checklist after each implement phase: naming conventions, locator rules, Playwright patterns, AAA structure, Allure decorators, code quality. **Cannot write or fix code — only reports issues.**

### `test-runner`
Runs `ruff`, `mypy`, and `pytest` on the phase files. Records every result. Escalates failures to the right place. **Cannot write or fix code.**

### `bug-tracer`
Receives a test failure, traces the call chain from test → fixture → page object → Playwright, and classifies the root cause. **Cannot fix code — only diagnoses.**

### `reporter`
Parses pytest output into a structured report: pass rate, slowest tests, flaky signals, coverage gaps.

### `maintainer`
Updates locator constants and page object methods when the app changes. Preserves test intent — never changes what a test asserts.

### `optimizer`
Analyzes the test suite for health issues: flaky patterns, slow tests, dead code, missing coverage.

---

## How Agents Communicate

Agents share state through two locations:

**`.claude/agents/` — machine-readable handoffs between agents**

| File | Written by | Read by |
|------|-----------|---------|
| `design.md` | `design` (via `/design_tests`) | `plan`, `implement`, `review` |
| `plan.md` | `plan` (via `/implement_tests`) | `implement`, `review`, `test-runner` |
| `review.md` | `review` | `test-runner` |
| `qa.md` | `test-runner` | — |

**`thoughts/` — human-readable outputs per command**

| Directory | Written by |
|-----------|-----------|
| `thoughts/requirements/` | `/requirements_review` |
| `thoughts/research/` | `/explore_codebase` |
| `thoughts/test-plans/` | `/test_plan` |
| `thoughts/test-designs/` | `/design_tests` |
| `thoughts/runs/` | `/run_tests` |
| `thoughts/debug/` | `/debug` |
| `thoughts/reports/` | `/reporting` |
| `thoughts/maintenance/` | `/maintenance` |
| `thoughts/optimization/` | `/optimization` |

---

## Quality Gates

Each stage has a gate — a condition that must be true before moving to the next stage.

| Stage | Gate |
|-------|------|
| Requirements Review | verdict = `READY` |
| Test Plan | Engineer approves scope, scenarios, and priorities |
| Design | Engineer approves page object + test case design |
| Implement (per phase) | review = `APPROVED` + all tests pass |
| Run Tests | all tests pass — if any fail, must go through Debug before proceeding |
| Debug | every failure has a diagnosis with confidence `MEDIUM` or `HIGH` |
| Apply Fixes | all previously failing tests now pass |
| Commit & PR | Engineer approves commit message and PR description |
| CI | all CI jobs pass — if any fail, re-enter Debug with the CI log |
| Maintenance | affected tests pass after update |

---

## Common Scenarios

### Adding a new page test from scratch
```
/requirements_review card "User can pay with a valid card. Payment succeeds and a confirmation is shown."
/test_plan card
/explore_codebase
/design_tests card accept-a-payment card page
/implement_tests card
/run_tests acceptapayment
/debug           # picks up latest run automatically
/apply_fixes acceptapayment
/reporting acceptapayment
/open_pr
```

### Something broke after a deploy
```
/run_tests acceptapayment
/debug           # picks up latest run automatically
/apply_fixes acceptapayment
/reporting acceptapayment
```

### App UI changed
```
/maintenance acceptapayment "card number input moved into a nested Stripe iframe"
```

### Monthly health check
```
/optimization all
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `/implement_tests` says no design found | Run `/design_tests <slug>` first |
| Tests fail immediately after writing | Run `/run_tests <app>`, then `/debug` |
| Selector stopped working | Run `/maintenance <app> <what changed>` |
| Suite is slow or flaky | Run `/optimization <app>` |
| CI fails but local passes | Run `/debug` with the exact failing node ID |
| Not sure what already exists | Run `/explore_codebase` |
| Requirement is vague | Run `/requirements_review` before anything else |
| Unsure what to test | Run `/test_plan <slug>` after requirements review |
