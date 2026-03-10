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

The QA Engineer never needs to write boilerplate, hunt for selectors, or manually trace test failures.

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
| 1 | Explore Codebase | triggers exploration, defines scope | reads files, maps structure, finds reusable patterns |
| 2 | Test Plan | approves or rejects scope, scenarios, and priorities | defines what to test: scope, scenarios, risks, coverage goals |
| 3 | Design | approves or rejects page object + test case design | proposes locators, methods, test scenarios |
| 4 | Implement | approves plan before code is written | writes page object, fixtures, test file |
| 5 | Debug | runs tests | reads output, traces root cause, fixes |
| 6 | Review | final approval | checks POM/AAA/FIRST compliance, flags issues |
| 7 | Commit & PR | approves commit message and PR description | stages files, writes message, opens PR |
| 8 | CI Execution | monitors pipeline | reads CI output, diagnoses env-specific failures |
| 9 | Reporting | reads report, decides next action | parses output, summarizes pass/fail/flaky/gaps |
| 10 | Maintenance | describes what changed in the app | traces broken tests, updates selectors/methods |
| 11 | Optimization | decides what to keep or drop | detects flaky/slow tests, flags redundant coverage |

**Key pattern:**
- **Engineer owns:** intent (requirements, approvals, decisions)
- **AI owns:** execution (reading, writing, running, analyzing)
- **Shared:** design and review — AI proposes/checks, Engineer approves/decides

---

## Full Command Sequence

For adding a new test from scratch, run commands in this order:

```
/requirements_review <slug> <requirement>    ← Is this testable?
/explore_codebase                            ← What already exists?
/test_plan <slug>                            ← What to test and why?
/design_tests <slug> <description>          ← Plan the page object + tests
/implement_tests <slug>                     ← Write the code
/debug <scope>                              ← Run tests, fix failures
/review <scope>                             ← Final POM/AAA/FIRST check
/open_pr                                    ← Stage files, write message, open PR
/ci [<pr-number>]                           ← Monitor pipeline, diagnose failures
/reporting <scope>                          ← Summary report
```

For ongoing work (no new tests):

```
/maintenance <app> <what changed>           ← App changed, fix broken tests
/optimization <scope>                       ← Suite health check
/reporting <scope>                          ← Report results
```

---

## Commands

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

### `/explore_codebase`

**Stage:** 1 — Explore Codebase

**When to use:** When the codebase structure is unfamiliar or a map of existing patterns is needed.

**What happens:**
1. Reads all page objects, base classes, fixtures, test files
2. Maps structure: class hierarchy, method patterns, locator conventions
3. Identifies reusable components

**Output:** `thoughts/research/YYYY-MM-DD-<topic>.md`

This runs automatically inside `/design_tests` too — run it separately only to explore without designing.

---

### `/test_plan <slug>`

**Stage:** 2 — Test Plan

**When to use:** After requirements are confirmed `READY` and the codebase is explored.

**What happens:**
1. Defines the scope: which pages, flows, and scenarios to cover
2. Lists specific test scenarios with priority (P1 / P2 / P3)
3. Identifies risks and coverage goals
4. Flags missing edge cases or out-of-scope items

**Output:** `thoughts/test-plans/YYYY-MM-DD-<slug>.md`

> ⚠️ The QA Engineer must approve the plan before moving to `/design_tests`.

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

**Prerequisite:** `.claude/agents/design.md` must exist.

**What happens:**
1. Checks that `design.md` exists — stops if not
2. Generates a phased plan (shows the phases, asks for confirmation)
3. For each phase:
   - Writes code: locators → page object → fixture → test file
   - Runs automated review (naming, POM, AAA, Playwright rules)
   - Runs tests (ruff, mypy, pytest)
   - Only moves to next phase when current phase passes all checks

**Output:** Code files in `pages/` and `tests/`

> ⚠️ Each phase requires review + test pass before proceeding. Failures are shown to the QA Engineer, who decides how to handle them.

---

### `/debug <scope>`

**Stage:** 5 — Debug

**When to use:** When tests are failing — after implementation, after a CI failure, or anytime investigation is needed.

Scope can be:
- App name: `the_internet`
- Test file: `tests/the_internet/test_login.py`
- Marker: `smoke`
- Node ID: `tests/the_internet/test_login.py::TestLogin::test_valid_login`

**What happens:**
1. Runs pytest with the given scope
2. If all pass → done
3. If failures → spawns a `bug-tracer` for each failure
4. Each failure is classified: `SELECTOR` / `TIMING` / `LOGIC` / `FIXTURE` / `ASSERTION` / `IMPORT` / `CONFIG` / `FLAKY` / `ENVIRONMENT`
5. Reports exact file + line + what needs to change
6. Asks the QA Engineer whether to apply the fixes

**Output:** `thoughts/debug/YYYY-MM-DD-<slug>.md`

---

### `/review <scope>`

**Stage:** 6 — Review

**When to use:** After implementation passes tests, before committing — to verify code quality against project standards.

Scope can be:
- App name: `the_internet`
- Test file: `tests/the_internet/test_login.py`
- Feature slug: `login`
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

**Stage:** 7 — Commit & PR

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
/maintenance the_internet "login button text changed from Login to Sign In"
/maintenance saucedemo "product items now have data-test attributes"
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

Agents pass information through files in `.claude/agents/`:

```
design.md   ← written by design agent, read by plan + implement + review
plan.md     ← written by plan agent, read by implement + review + test-runner
review.md   ← written by review agent, read by test-runner
qa.md       ← written by test-runner
```

And to `thoughts/` for human-readable outputs:

```
thoughts/requirements/    ← requirements_review output
thoughts/research/        ← explore_codebase output
thoughts/test-plans/      ← test_plan output
thoughts/test-designs/    ← design_tests output
thoughts/debug/           ← debug output
thoughts/reports/         ← reporting output
thoughts/maintenance/     ← maintenance output
thoughts/optimization/    ← optimization output
```

---

## Quality Gates

Each stage has a gate — a condition that must be true before moving to the next stage.

| Stage | Gate |
|-------|------|
| Requirements Review | verdict = `READY` |
| Test Plan | Engineer approves scope, scenarios, and priorities |
| Design | Engineer approves page object + test case design |
| Implement (per phase) | review = `APPROVED` + all tests pass |
| Debug | all tests in scope pass |
| Maintenance | affected tests pass after update |

---

## Common Scenarios

### Adding a new page test from scratch
```
/requirements_review checkboxes "User can check and uncheck checkboxes. State should reflect correctly."
/explore_codebase
/test_plan checkboxes
/design_tests checkboxes the-internet checkboxes page
/implement_tests checkboxes
/debug the_internet
/reporting the_internet
/open_pr
```

### Something broke after a deploy
```
/debug the_internet
# → shows failures with root cause
# → apply fixes or fix manually
/reporting the_internet
```

### App UI changed
```
/maintenance the_internet "checkbox inputs now have id=checkbox-1 and id=checkbox-2"
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
| Tests fail immediately after writing | Run `/debug <app>` |
| Selector stopped working | Run `/maintenance <app> <what changed>` |
| Suite is slow or flaky | Run `/optimization <app>` |
| CI fails but local passes | Run `/debug` with the exact failing node ID |
| Not sure what already exists | Run `/explore_codebase` |
| Requirement is vague | Run `/requirements_review` before anything else |
| Unsure what to test | Run `/test_plan <slug>` after requirements review |
