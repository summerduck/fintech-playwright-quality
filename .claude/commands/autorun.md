# Autorun Command

You are an autonomous QA orchestrator. You run the full test-building pipeline end-to-end — from requirements to working, passing tests — without asking for human approval at intermediate stages.

**You make all gate decisions yourself.** You only stop and surface a question to the QA Engineer when you hit something that is genuinely unresolvable: contradictory requirements, a persistent test failure you cannot diagnose with HIGH or MEDIUM confidence, or a codebase ambiguity that would force you to guess architecture.

**IMPORTANT — spawn all subagents with `mode: "bypassPermissions"`** to prevent Bash approval prompts from blocking the autonomous pipeline. Every Agent tool call in this command must include `mode: "bypassPermissions"`.

---

## Arguments

`$ARGUMENTS`

- `$ARGUMENTS[0]` — feature slug (e.g. `login`, `checkboxes`, `drag-drop`)
- `$ARGUMENTS[1+]` — requirement text, ticket, or user story

If no requirement text is provided, ask once:
> What should I test? Paste the requirement or describe the feature.

---

## Stage 0 — Clean Run Directory

Run: `rm -f .claude/agent-memory-local/*.md`

This removes stale handoff files from any previous session before the new pipeline starts.

---

## Stage 1 — Requirements Review

Spawn `requirements/agent-memory-local/ewer` subagent.

Pass: the requirement text. **Do not save output to `thoughts/`** — keep results in memory only.

**Autonomous gate decision:**
- Verdict `READY` → proceed to Stage 2.
- Verdict `NEEDS CLARIFICATION` → read the open questions. Attempt to answer each question using the codebase and the requirement text. Document your assumptions inline. Proceed to Stage 2 with those assumptions noted.
- Verdict `NOT TESTABLE` → **STOP.** Surface to QA Engineer:
  > Cannot proceed — requirement is not testable: `<reason>`. Please revise and re-run.

---

## Stage 2 — Test Plan

Spawn `test-planner` subagent.

Pass: slug + requirement text + requirements review findings (from memory). **Do not save output to `thoughts/`** — keep results in memory only.

**Autonomous gate decision:**
- Verdict `READY FOR DESIGN` → proceed to Stage 3.
- Verdict `NEEDS CLARIFICATION` → resolve open questions using the requirement text and your best judgment. Document assumptions. Proceed.

---

## Stage 3 — Explore Codebase

Spawn **3 parallel** `codebase-explorer` subagents:

**Task 1:** Architecture — base classes, app structure, existing page objects for this app.

**Task 2:** Fixtures & tests — conftest.py fixtures, marker definitions in pyproject.toml, existing test patterns.

**Task 3:** Reuse candidates — any existing page object, locator, or workflow relevant to the slug.

Wait for all 3. Consolidate findings into a research summary — keep in memory for Stage 4, do not save to `thoughts/`.

---

## Stage 4 — Design

Spawn `design` subagent.

Pass:
- Feature slug and description
- Research summary from Stage 3 (from memory)
- Test plan findings from Stage 2 (from memory)

**Do not save design output to `thoughts/`** — save only to `.claude/agent-memory-local/design.md`.

**Autonomous gate decision:**
- Design document produced and all sections populated → proceed to Stage 5.
- Design has missing sections or unresolved deviations from existing patterns → spawn `design` subagent once more with the gaps noted. If still incomplete after 2 attempts → **STOP and surface to QA Engineer.**

---

## Stage 5 — Implement (phase by phase)

### 5a. Plan

Spawn `plan` subagent.

Pass: design document (`.claude/agent-memory-local/design.md`) + research summary + slug.

**Do not save plan output to `thoughts/`** — save only to `.claude/agent-memory-local/plan.md`.

Read the generated `plan.md` to know how many phases there are.

### 5b. For each phase in plan.md

Run this loop (max 3 correction/agent-memory-local/es per phase before stopping):

**Step 1 — Implement**/agent-memory-local/

Spawn `implement` subagent.

Pass: current phase from `plan.md` + full `plan.md` + `design.md`.

**Step 2 — Review**

Spawn `review` subagent.

Pass: files changed in this phase + `plan.md` + `design.md`. **Do not save review output to `thoughts/`** — save only to `.claude/agent-memory-local/review.md`.

Read `.claude/agent-memory-local/review.md`.

**Autonomous gate decision:**
- `APPROVED` → go to Step 3.
- `CHANGES REQUIRED` → pass the issues list back to `implement` subagent. Re-run review. Repeat up to **2 more times**.
- Still `CHANGES REQUIRED` after 3 total cycles → **STOP.** Surface to QA Engineer:
  > Phase `<N>` — `<name>` cannot be auto-approved after 3 cycles. Unresolved issues:/agent-memory-local/
  > `<issue list>`
/agent-memory-local/
**Step 3 — Static analysis + targeted tests**

Spawn `test-runner` subagent (phase mode).

Pass: test files for this phase + `plan.md` + `review.md`. **Do not save QA output to `thoughts/`** — save only to `.claude/agent-memory-local/qa.md`.

**Autonomous gate decision:**
- `ALL PASSED` → phase complete. Move to next phase.
- `BLOCKED BY STATIC ANALYSIS` → pass ruff/mypy errors to `implement` subagent. Re-run review + test-runner. Up to **2 retries**.
- `FAILURES DETECTED` → pass failure output to `implement` subagent via the `review` agent routing (assertion errors → review → implement; import/fixture errors → implement directly). Re-run. Up to **2 retries**.
- Still failing after retries → **STOP.** Surface to QA Engineer with full failure output.

---/agent-memory-local/

## Stage 6 — Run Full Test Suite

After all phases complete, run the full test suite for the app:

```bash
pytest tests/<app>/ -v --no-header --tb=short
```

Keep raw output in memory — do not save to `thoughts/`.

**Autonomous gate decision:**
- All pass → proceed to Stage 7 (report only).
- Failures → proceed to Stage 6b.

---

## Stage 6b — Debug Failures (if any)

Spawn one `bug-tracer` subagent per failing test (up to 3 in parallel, sequential beyond that).

For each diagnosis:

- Confidence `HIGH` or `MEDIUM` → proceed to fix automatically.
- Confidence `LOW` or `INCONCLUSIVE` → **STOP for this failure.** Surface to QA Engineer:
  > Cannot diagnose `<node ID>` with sufficient confidence: `<reason>`. Manual investigation needed.

Spawn `implement` subagent with fix instructions for all HIGH/MEDIUM diagnoses.

Rerun only the previously failing tests.

**Autonomous gate decision:**
- All fixed tests now pass → proceed to Stage 7.
- Still failing after fix → attempt one more debug/fix cycle.
- Still failing after 2 total cycles → **STOP.** Surface to QA Engineer with full output.

---

## Stage 7 — Final Report

Spawn `reporter` subagent.

Pass: final pytest output (from memory) + list of all test files for the app. **Do not save report to `thoughts/`** — present summary directly in the conversation.

Present the summary to the QA Engineer:

```
Autorun complete — <slug>

Stages completed: 0:Clean → 1:Requirements → 2:TestPlan → 3:Explore → 4:Design → 5:Implement → 6:Tests

Files created:
- <path>

Test results:
  Pass rate: N%
  Tests: N passed, N failed, N skipped

Assumptions made (resolve if incorrect):
- <any assumptions from NEEDS CLARIFICATION stages>

Next step: run `/review <scope>` for a final manual check, then `/open_pr`.
```

If any tests are still failing, end with:
```
⚠ Unresolved failures — manual investigation required:
- <node ID>: <reason it could not be auto-fixed>
```
