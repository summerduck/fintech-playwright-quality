# Implement Tests Command

You are coordinating the implementation of E2E tests from an approved design document.

**Core principle:** No code is written until the plan is confirmed. Work phase by phase.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — feature slug (e.g. `login`, `drag-drop`)
---

## Phase 2: Verify Prerequisites + Plan

Before doing anything:

1. Clean the run directory: `rm -f .claude/agent-memory-local/*.md` — removes stale files from any previous session.

2. Check that a design document exists: look for `thoughts/test-designs/YYYY-MM-DD-<slug>.md` (most recent matching the slug), or fall back to `.claude/agent-memory-local/design.md`. If neither exists, stop and say:
   > No design document found. Run `/design_tests <slug>` first.

3. Read the design document completely. Copy it to `.claude/agent-memory-local/design.md` so downstream agents read from a fixed path.

4. Spawn the `plan` subagent (Agent tool with `subagent_type: "plan"`):
   - Pass: the full design document content, the feature slug, and instruction to save to `.claude/agent-memory-local/plan.md`
   - Wait for completion, then read `.claude/agent-memory-local/plan.md`

4. Present design summary + plan to the user in a **single confirmation**:
   > Design: `<feature>` — `<N files to create/modify>`, `<N test cases>`
   > Plan: `<N>` phases:
   > - Phase 1: <name>
   > - Phase 2: <name>
   > ...
   > Proceed?

Wait for one confirmation before continuing.

---

## Phase 3: Implement Phase by Phase

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

4. If review status is `APPROVED`: confirm phase complete and move to next.

**Do NOT run tests after each phase.** Collect all changed/created files across all phases. Run tests once after all phases are approved (see Phase 4).

---

## Phase 4: Run Tests Once

After all phases are approved, spawn ONE `test-runner` subagent:
- Pass: the full list of test files touched across all phases
- Wait for completion
- If QA fails: show failure output and ask user how to proceed
- If QA passes: proceed to final summary

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
