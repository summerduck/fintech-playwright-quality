# Multi-Agent E2E Workflow

This document describes the end-to-end process for adding a new E2E test feature using the agent system defined in `.claude/agents/`.

---

## How to Start

Provide a task description to Lead Agent. Example:

> "Add E2E tests for the Checkboxes page on The Internet app. Verify that checkboxes can be checked and unchecked, and that their state persists correctly."

Lead Agent orchestrates the rest. Do not skip stages or bypass the quality gates.

---

## Stage 1 — Research

**Agent:** Research Agent
**Prompt file:** `.claude/agents/research.md`
**Input:** Task description only
**Output:** `.claude/agents/research.md` (overwritten with facts)

What happens:
- Research Agent reads `pages/`, `tests/`, `config/`, `conftest.py`, `pyproject.toml`, `utils/`.
- Produces a factual inventory: files, classes, methods, fixtures, markers, browser config.
- Reports only what is present — no opinions or suggestions.

Gate before proceeding:
- `research.md` contains at minimum: page objects list, test files list, fixtures list, markers list, browser config.

---

## Stage 2 — Design

**Agent:** Design Agent
**Prompt file:** `.claude/agents/design.md`
**Input:** `research.md` + task description
**Output:** `.claude/agents/design.md` (overwritten with architecture)

What happens:
- Design Agent maps the task to the project's containers (pages, tests, fixtures, config).
- Specifies exactly: new file paths, class names, `URL_PATH`, `APP_NAME`, method names, locator strategies.
- Defines data flow from fixture → page object → Playwright → assertion.
- States naming conventions and Playwright usage rules that apply to this task.

Gate before proceeding:
- `design.md` contains: Context, Containers, Components (with file paths and class names), Data Flow, Naming Conventions, Playwright Rules.
- No code is present in `design.md` — only specifications.

---

## Stage 3 — Plan

**Agent:** Plan Agent
**Prompt file:** `.claude/agents/plan.md`
**Input:** `research.md` + `design.md` + task description
**Output:** `.claude/agents/plan.md` (overwritten with phased plan)

What happens:
- Plan Agent divides the work into 2–5 phases.
- Each phase defines: goal, files to create or change, constraints, acceptance criteria.
- Produces a review checklist for Review Agent specific to this task.
- Produces instructions for Implement Agent.

Typical phases:
```
Phase 1: Page Object(s) — locators + page class
Phase 2: Core happy-path tests
Phase 3: Edge cases and negative scenarios
Phase 4: Smoke test annotation (if applicable)
```

Gate before proceeding:
- `plan.md` contains at least one phase with: goal, file table, constraints, acceptance criteria.
- The review checklist section is present.

---

## Stage 4 — Implement (per phase)

**Agent:** Implement Agent
**Prompt file:** `.claude/agents/implement.md`
**Input:** `plan.md` (current phase) + `design.md`
**Output:** Code files listed in the current phase

What happens:
- Implement Agent works on exactly one phase at a time.
- Creates or modifies only the files listed in the current phase of `plan.md`.
- Follows the code standards in `implement.md` exactly.
- Reports back to Lead Agent with a list of created/changed files and acceptance criteria status.

Order within each phase:
```
1. locators.py  (add new constants)
2. <feature>_page.py  (page object class)
3. conftest.py  (add fixture)
4. test_<feature>.py  (test file)
```

Gate before proceeding to Review:
- All files in the phase exist on disk.
- Implement Agent confirms acceptance criteria are met.

---

## Stage 5 — Review (per phase)

**Agent:** Review Agent
**Prompt file:** `.claude/agents/review.md`
**Input:** `plan.md` + `design.md` + changed files
**Output:** `.claude/agents/review.md` (overwritten with review report)

What happens:
- Review Agent runs through the universal checklist in `review.md`.
- Checks naming, locators, hardcoded values, Playwright patterns, Allure decorators, test body rules, code quality.
- Produces a report: `APPROVED` or `CHANGES REQUIRED`.
- For every failing item: file, line, rule, problem description, fix instruction.

Gate before proceeding to QA:
- `review.md` shows `Status: APPROVED`.
- If `CHANGES REQUIRED`: send back to Implement Agent with the full issue list. Repeat Stage 4 → Stage 5.

---

## Stage 6 — QA (per phase)

**Agent:** QA Agent
**Prompt file:** `.claude/agents/qa.md`
**Input:** `plan.md` + `review.md` + list of test files
**Output:** `.claude/agents/qa.md` (overwritten with QA report)

What happens:

1. Pre-run gate: confirms `review.md` is `APPROVED` and all files exist.
2. Static analysis: runs `ruff` and `mypy` on changed files.
3. Targeted test run: runs only the tests from the current phase.
4. Records every test result (node ID, PASSED/FAILED/ERROR/SKIPPED, duration).
5. For failures: records full traceback from `--tb=short`.
6. Produces QA report with summary and escalation recommendation.

Escalation:
- `ruff`/`mypy` errors → Implement Agent.
- Collection errors → Implement Agent.
- Test failures → Review Agent (who routes to Implement Agent if code fix is needed).

Gate before Lead Agent approval:
- `qa.md` shows `Status: ALL PASSED`.
- No tests in scope are FAILED, ERROR, or unexplained SKIPPED.

---

## Stage 7 — Lead Agent Approval

**Agent:** Lead Agent
**Input:** `qa.md` with `Status: ALL PASSED`

What happens:
- Lead Agent confirms all stages completed with passing gates.
- Summarises: which files were created or changed, which phases were completed.
- States: **"Ready for merge."**

If any gate failed at any stage, Lead Agent routes back to the appropriate agent with the reason.

---

## Repeat for Each Phase

Stages 4 → 5 → 6 repeat for each phase defined in `plan.md`. Lead Agent does not approve the full task until all phases have passed QA.

```
Phase 1: Implement → Review → QA → (approved) →
Phase 2: Implement → Review → QA → (approved) →
...
Phase N: Implement → Review → QA → (approved) →
Lead Agent: "Ready for merge."
```

---

## Document Map

| File | Written by | Read by |
|---|---|---|
| `.claude/agents/research.md` | Research Agent | Design Agent, Plan Agent |
| `.claude/agents/design.md` | Design Agent | Plan Agent, Implement Agent, Review Agent |
| `.claude/agents/plan.md` | Plan Agent | Implement Agent, Review Agent, QA Agent |
| `.claude/agents/review.md` | Review Agent | QA Agent, Lead Agent |
| `.claude/agents/qa.md` | QA Agent | Lead Agent |

---

## Troubleshooting

| Symptom | Action |
|---|---|
| Implement Agent cannot find a file mentioned in `design.md` | Report to Lead Agent → Lead Agent asks user |
| Review Agent finds an issue that requires changing `design.md` | Lead Agent restarts from Design Agent |
| QA tests fail due to environment (network, browser crash) | Re-run once; if still failing, report to Lead Agent as infrastructure issue |
| `mypy` reports errors in existing (unchanged) files | Report to Lead Agent; do not fix unless the current phase changed those files |
| Plan phases are ambiguous | Lead Agent asks user to clarify before continuing |
