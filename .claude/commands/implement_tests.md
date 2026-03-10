# Implement Tests Command

You are coordinating the implementation of E2E tests from an approved design document.

**Core principle:** No code is written until the plan is confirmed. Work phase by phase.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — feature slug (e.g. `login`, `drag-drop`)
---

## Phase 2: Verify Prerequisites

Before doing anything:

1. Check that a design document exists: look for `thoughts/test-designs/YYYY-MM-DD-<slug>.md` (most recent matching the slug), or fall back to `.claude/agents/design.md`. If neither exists, stop and say:
   > No design document found. Run `/design_tests <slug>` first.

2. Read the design document completely.

3. Confirm with the user:
   > I found the design for `<feature>`. It covers:
   > - Page object: `<class name>` in `<file path>`
   > - Tests: `<N>` test cases
   > - App: `<app name>`
   >
   > Proceed with implementation?

Wait for confirmation before continuing.

---

## Phase 3: Plan

Spawn the `plan` subagent (Agent tool with `subagent_type: "plan"`):

Pass:
- The design document content
- The feature slug
- Instruction: produce `plan.md` at `.claude/agents/plan.md`

Wait for plan to complete. Read `.claude/agents/plan.md`.

Present the phase breakdown to the user:
> Plan ready. Phases:
> - Phase 1: <name>
> - Phase 2: <name>
> ...
> Proceed?

Wait for approval.

---

## Phase 4: Implement Phase by Phase

For each phase in `plan.md`:

1. Spawn the `implement` subagent (Agent tool with `subagent_type: "implement"`):
   - Pass: current phase description + `plan.md` + `design.md`
   - Wait for completion

2. Spawn the `review` subagent (Agent tool with `subagent_type: "review"`):
   - Pass: list of files changed in this phase + `plan.md` + `design.md`
   - Wait for completion
   - Read review result

3. If review status is `CHANGES REQUIRED`:
   - Show issues to user
   - Re-spawn `implement` subagent with the review feedback
   - Re-run review
   - Repeat until `APPROVED` (max 2 cycles — escalate to user if still failing)

4. If review status is `APPROVED`:
   - Spawn `qa` subagent (Agent tool with `subagent_type: "test-runner"`):
     - Pass: list of test files for this phase
     - Wait for completion
   - If QA fails: show failure output and ask user how to proceed
   - If QA passes: confirm phase complete and move to next

---

## Phase 5: Final Summary

After all phases pass:

```
Implementation complete.

Files created:
- <path>

Files changed:
- <path>

All phases: APPROVED and PASSING

Next step: run `/reporting <app>` to get a full suite report.
```
