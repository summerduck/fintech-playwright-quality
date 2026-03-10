# Test Plan Command

You are a QA lead creating a test plan for a feature before design begins.

**Core principle:** Define what to test — scope, scenarios, priorities — before deciding how to implement anything.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — feature slug (e.g. `login`, `drag-drop`)
- `$ARGUMENTS[1+]` — optional description or notes

If no feature slug is provided, ask:
> What feature or page are you planning tests for?

---

## Phase 2: Locate Prior Outputs

Check for existing artifacts from earlier stages:

1. Look in `thoughts/requirements/` for a file matching the feature slug.
2. Look in `thoughts/research/` for a file matching the feature slug.

Pass the paths of any found files to the agent. If neither exists, proceed — the agent will work from the feature description alone and flag the gaps.

---

## Phase 3: Run the Test Planner

Spawn the `test-planner` subagent (Agent tool with `subagent_type: "test-planner"`):

Pass:
- The feature slug
- The feature description (if provided)
- Paths to any requirements or research files found in Phase 2
- Instruction to save output to `thoughts/test-plans/YYYY-MM-DD-<slug>.md`

Wait for the agent to complete.

---

## Phase 4: Present the Plan

After the agent completes, present to the user:

1. **Scope** — what is in and out of scope
2. **Test scenarios** — full table with IDs, priorities, and notes
3. **Risks & gaps** — anything that blocks or limits automation
4. **Open questions** — anything requiring engineer input

If verdict is READY FOR DESIGN:
> Test plan is ready. Run `/design_tests <slug>` to begin page object and test case design.

If verdict is NEEDS CLARIFICATION:
> Please answer the open questions above before proceeding to design.
