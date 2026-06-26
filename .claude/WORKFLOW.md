# E2E Test Automation Workflow

This document describes the end-to-end process for adding, running, and maintaining E2E tests using the command system in `.claude/commands/`.

---

## Command Sequence

Run commands in this order. Each command is a self-contained stage — complete one before starting the next.

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

## Stage 0 — Requirements Review

**Command:** `/requirements_review <slug> <requirement>`
**Agent:** `requirements-reviewer`
**Output:** `thoughts/requirements/YYYY-MM-DD-<slug>.md`

Checks testability, flags ambiguities, identifies missing edge cases.
Gate: verdict must be `READY` before proceeding to test plan.

---

## Stage 1 — Test Plan

**Command:** `/test_plan <slug>`
**Agent:** `test-planner`
**Output:** `thoughts/test-plans/YYYY-MM-DD-<slug>.md`

Defines scope, test scenarios with priority (P1/P2/P3), risks, and coverage goals.
Gate: QA Engineer must approve scope, scenarios, and priorities before proceeding.

---

## Stage 2 — Explore Codebase

**Command:** `/explore_codebase`
**Agent:** `codebase-explorer`
**Output:** `thoughts/research/YYYY-MM-DD-<topic>.md`

Maps existing page objects, fixtures, base classes, and conventions.
Use when the codebase structure is unfamiliar or when designing for a new app.
Also runs automatically inside `/design_tests`.

---

## Stage 3 — Design

**Command:** `/design_tests <slug> <description>`
**Agents:** `codebase-explorer`, `design`, `plan`
**Output:** `thoughts/test-designs/YYYY-MM-DD-<slug>.md`, `.claude/agent-memory-local/design.md`

Proposes page object structure, locators, methods, and test cases.
Gate: QA Engineer must approve the design before implementation begins.

---

## Stage 4 — Implement

**Command:** `/implement_tests <slug>`
**Agents:** `plan`, `implement`, `review`, `test-runner`
**Output:** Code files in `pages/` and `tests/`

Prerequisite: `thoughts/test-designs/YYYY-MM-DD-<slug>.md` must exist (produced by `/design_tests`).
Works phase by phase: each phase goes through Implement → Review → Test Runner before proceeding.

Implementation order within each phase:
```
1. pages/<app>/locators.py        (new constants)
2. pages/<app>/<feature>_page.py  (page object)
3. tests/<app>/conftest.py        (fixture)
4. tests/<app>/test_<feature>.py  (test file)
```

---

## Stage 5 — Run Tests

**Command:** `/run_tests <scope>`
**Agent:** `test-runner`
**Output:** `thoughts/runs/YYYY-MM-DD-<scope-slug>.txt`

Runs tests for the given scope and produces the raw pytest output.
If all pass → proceed to reporting. If failures → pass the output to `/debug`.

Scope can be: app name, test file, marker, or node ID.

---

## Stage 6 — Debug

**Command:** `/debug [<output>]`
**Agent:** `bug-tracer`
**Output:** `thoughts/debug/YYYY-MM-DD-<slug>.md`

If called with no argument, automatically reads all known output locations: `thoughts/runs/`, `test-logs/`, `test-results/failed_tests/`, `report.html`, `allure-report/`.

Diagnoses failures by category (`SELECTOR` / `TIMING` / `LOGIC` / `FIXTURE` / `ASSERTION` / `IMPORT` / `CONFIG` / `FLAKY` / `ENVIRONMENT`). Reports exact file + line + what needs to change. Does not apply fixes.

Gate: every failure must have a diagnosis with confidence `MEDIUM` or `HIGH`.

---

## Stage 7 — Apply Fixes

**Command:** `/apply_fixes <scope>`
**Agents:** `implement`, `test-runner`
**Output:** Updated files in `pages/` and/or `tests/`

Prerequisite: a debug report in `thoughts/debug/` for the given scope (produced by `/debug`).
Reads each diagnosed failure, delegates the fix to `implement`, and reruns the affected tests to confirm resolution.

---

## Stage 8 — Review

**Command:** `/review <scope>`
**Agent:** `review`
**Output:** Review result with `file:line` references for every issue

After implementation passes tests, before committing. Checks: POM structure, AAA pattern, FIRST principles, Playwright patterns, naming conventions, Allure decorators, locator quality.

Issues are grouped by severity (HIGH / MEDIUM / LOW).
Gate: HIGH severity issues must be resolved before `/open_pr`.

Scope can be: app name, test file, feature slug, or omit to review all files changed since last commit.

---

## Stage 9 — Commit & PR

**Command:** `/open_pr`
**Output:** PR URL

Nothing is committed or pushed without explicit QA Engineer approval of both the commit message and PR description.

---

## Stage 10 — CI Execution

**Command:** `/ci [<pr-number>]`
**Output:** `thoughts/debug/YYYY-MM-DD-ci-<slug>.md`

Monitors the pipeline and diagnoses failures. If CI jobs fail, classifies failures and recommends fixes.

> Full CI automation is pending MCP integration. Current usage requires manual monitoring.

---

## Stage 11 — Reporting

**Command:** `/reporting <scope>`
**Agent:** `reporter`
**Output:** `thoughts/reports/YYYY-MM-DD-<scope>.md`

Parses pytest output into structured pass/fail/flaky/gap report.

---

## Stage 12 — Maintenance

**Command:** `/maintenance <app> <description of change>`
**Agents:** `codebase-explorer`, `maintainer`
**Output:** `thoughts/maintenance/YYYY-MM-DD-<slug>.md`

Updates selectors and page object methods when the app changes. Does not change test intent.

---

## Stage 13 — Optimization

**Command:** `/optimization <scope>`
**Agents:** `optimizer`, `maintainer`
**Output:** `thoughts/optimization/YYYY-MM-DD-<scope>.md`

Detects flaky tests, slow tests, dead code, and coverage gaps.

---

## Document Map

**`.claude/agents/` — agent definition files (never written to during runs)

**`.claude/agent-memory-local/` — machine-readable pipeline handoffs (overwritten each run)****

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
| `thoughts/test-plans/` | `/test_plan` |
| `thoughts/research/` | `/explore_codebase` |
| `thoughts/test-designs/` | `/design_tests` |
| `thoughts/plans/` | `plan` agent (via `/implement_tests`) |
| `thoughts/reviews/` | `review` agent (via `/implement_tests`, `/review`) |
| `thoughts/qa/` | `test-runner` agent (via `/implement_tests`) |
| `thoughts/runs/` | `/run_tests` |
| `thoughts/debug/` | `/debug` |
| `thoughts/reports/` | `/reporting` |
| `thoughts/maintenance/` | `/maintenance` |
| `thoughts/optimization/` | `/optimization` |

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
/debug
/apply_fixes acceptapayment
/reporting acceptapayment
/open_pr
```

### Something broke after a deploy
```
/run_tests acceptapayment
/debug
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
| Tests fail immediately after writing | Run `/run_tests <app>`, then `/debug`, then `/apply_fixes <app>` |
| Selector stopped working | Run `/maintenance <app> <what changed>` |
| Suite is slow or flaky | Run `/optimization <app>` |
| CI fails but local passes | Run `/debug` with the exact failing node ID |
| Not sure what already exists | Run `/explore_codebase` |
| Requirement is vague | Run `/requirements_review` before anything else |
| Unsure what to test | Run `/test_plan <slug>` after requirements review |
| `ruff` errors in unchanged files | Do not fix — report and skip |
