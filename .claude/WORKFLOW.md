# E2E Test Automation Workflow

This document describes the end-to-end process for adding, running, and maintaining E2E tests using the command system in `.claude/commands/`.

---

## Command Sequence

Run commands in this order. Each command is a self-contained stage — complete one before starting the next.

```
/requirements_review <slug> <requirement text>
        ↓
/explore_codebase
        ↓
/design_tests <slug> <description>
        ↓
/implement_tests <slug>
        ↓
/run_tests <scope>
        ↓
/debug <output>
        ↓
/apply_fixes <scope>
        ↓
/reporting <app>
        ↓
/open_pr
```

---

## Stage 0 — Requirements Review

**Command:** `/requirements_review <slug> <requirement>`
**Agent:** `requirements-reviewer`
**Output:** `thoughts/requirements/YYYY-MM-DD-<slug>.md`

Checks testability, flags ambiguities, identifies missing edge cases.
Gate: verdict must be `READY` before proceeding to design.

---

## Stage 1 — Explore Codebase

**Command:** `/explore_codebase`
**Agent:** `codebase-explorer`
**Output:** `thoughts/research/YYYY-MM-DD-<topic>.md`

Maps existing page objects, fixtures, base classes, and conventions.
Use when the codebase structure is unfamiliar or when designing for a new app.

---

## Stage 2 — Design

**Command:** `/design_tests <slug> <description>`
**Agents:** `codebase-explorer`, `design`, `plan`
**Output:** `thoughts/test-designs/YYYY-MM-DD-<slug>.md`, `.claude/agents/design.md`

Proposes page object structure, locators, methods, and test cases.
Gate: user must approve the design before implementation begins.

---

## Stage 3 — Implement

**Command:** `/implement_tests <slug>`
**Agents:** `plan`, `implement`, `review`, `test-runner`
**Output:** code files + `.claude/agents/plan.md`

Prerequisite: `.claude/agents/design.md` must exist (produced by `/design_tests`).
Works phase by phase: each phase goes through Implement → Review → Test Runner before proceeding.

Implementation order within each phase:
```
1. pages/<app>/locators.py     (new constants)
2. pages/<app>/<feature>_page.py  (page object)
3. tests/<app>/conftest.py     (fixture)
4. tests/<app>/test_<feature>.py  (test file)
```

---

## Stage 4 — Run Tests

**Command:** `/run_tests <scope>`
**Agent:** `test-runner`
**Output:** `thoughts/runs/YYYY-MM-DD-<scope-slug>.txt`

Runs tests for the given scope and produces the raw pytest output.
If all pass → proceed to reporting. If failures → pass the output to `/debug`.

---

## Stage 5 — Debug

**Command:** `/debug <output>`
**Agents:** `bug-tracer`
**Output:** `thoughts/debug/YYYY-MM-DD-<slug>.md`

Accepts pytest output from `/run_tests`, diagnoses failures by category (SELECTOR, TIMING, LOGIC, FIXTURE, etc.), and produces fix instructions. Does not apply fixes.

---

## Stage 6 — Apply Fixes

**Command:** `/apply_fixes <scope>`
**Agents:** `implement`, `test-runner`
**Output:** Updated files in `pages/` and/or `tests/`

Prerequisite: a debug report in `thoughts/debug/` for the given scope (produced by `/debug`).
Reads each diagnosed failure, delegates the fix to `implement`, and reruns the affected tests to confirm resolution.

---

## Stage 7 — Review

Review is embedded inside `/implement_tests` — the `review` agent runs automatically after each phase. No separate command needed.

---

## Stage 8 — Commit & PR

Use the built-in `/commit` command to stage files, write a commit message, and open a PR.

---

## Stage 9 — CI Execution

Manual — monitor the pipeline. If CI fails, run `/debug` with the failing test scope.

---

## Stage 10 — Reporting

**Command:** `/reporting <scope>`
**Agent:** `reporter`
**Output:** `thoughts/reports/YYYY-MM-DD-<scope>.md`

Parses pytest output into structured pass/fail/flaky/gap report.

---

## Stage 11 — Maintenance

**Command:** `/maintenance <app> <description of change>`
**Agents:** `codebase-explorer`, `maintainer`
**Output:** `thoughts/maintenance/YYYY-MM-DD-<slug>.md`

Updates selectors and page object methods when the app changes. Does not change test intent.

---

## Stage 12 — Optimization

**Command:** `/optimization <scope>`
**Agents:** `optimizer`, `maintainer`
**Output:** `thoughts/optimization/YYYY-MM-DD-<scope>.md`

Detects flaky tests, slow tests, dead code, and coverage gaps.

---

## Document Map

| File | Written by | Read by |
|------|-----------|---------|
| `.claude/agents/design.md` | `design` agent (via `/design_tests`) | `/implement_tests` |
| `.claude/agents/plan.md` | `plan` agent (via `/implement_tests`) | `implement`, `review`, `test-runner` agents |
| `.claude/agents/review.md` | `review` agent | `test-runner` agent |
| `.claude/agents/qa.md` | `test-runner` agent | — |

---

## Troubleshooting

| Symptom | Action |
|---------|--------|
| `/implement_tests` says no design found | Run `/design_tests <slug>` first |
| Test fails after implementation | Run `/run_tests <app>`, then `/debug <output>`, then `/apply_fixes <app>` |
| Selector broke after app update | Run `/maintenance <app> <what changed>` |
| Suite is slow or flaky | Run `/optimization <app>` |
| `mypy`/`ruff` errors in unchanged files | Do not fix — report and skip |
