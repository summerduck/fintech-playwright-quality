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
/run_and_debug <app>
        ↓
/reporting <app>
        ↓
/commit
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

## Stage 4 — Run & Debug

**Command:** `/run_and_debug <scope>`
**Agents:** `bug-tracer`, `implement`
**Output:** `thoughts/debug/YYYY-MM-DD-<slug>.md`

Runs tests, diagnoses failures by category (SELECTOR, TIMING, LOGIC, FIXTURE, etc.), and optionally applies fixes.

---

## Stage 5 — Review

Review is embedded inside `/implement_tests` — the `review` agent runs automatically after each phase. No separate command needed.

---

## Stage 6 — Commit & PR

Use the built-in `/commit` command to stage files, write a commit message, and open a PR.

---

## Stage 7 — CI Execution

Manual — monitor the pipeline. If CI fails, run `/run_and_debug` with the failing test scope.

---

## Stage 8 — Reporting

**Command:** `/reporting <scope>`
**Agent:** `reporter`
**Output:** `thoughts/reports/YYYY-MM-DD-<scope>.md`

Parses pytest output into structured pass/fail/flaky/gap report.

---

## Stage 9 — Maintenance

**Command:** `/maintenance <app> <description of change>`
**Agents:** `codebase-explorer`, `maintainer`
**Output:** `thoughts/maintenance/YYYY-MM-DD-<slug>.md`

Updates selectors and page object methods when the app changes. Does not change test intent.

---

## Stage 10 — Optimization

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
| Test fails after implementation | Run `/run_and_debug <app>` |
| Selector broke after app update | Run `/maintenance <app> <what changed>` |
| Suite is slow or flaky | Run `/optimization <app>` |
| `mypy`/`ruff` errors in unchanged files | Do not fix — report and skip |
