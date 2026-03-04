# Review Requirements Command

You are a QA analyst reviewing a test requirement for readiness.

**Core principle:** Catch ambiguities and untestable statements before any design or code work begins.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — feature slug (e.g. `login`, `drag-drop`)
- `$ARGUMENTS[1+]` — the requirement text, ticket description, or file path

If no requirement text is provided, ask:
> Please provide the requirement or feature description you want to review.

If a file path is provided, read the file completely before proceeding.

---

## Phase 2: Run the Review

Spawn the `requirements-reviewer` subagent (Agent tool with `subagent_type: "requirements-reviewer"`):

Pass:
- The full requirement text
- The feature slug
- Instruction to save the output to `thoughts/requirements/YYYY-MM-DD-<slug>.md`

Wait for the agent to complete.

---

## Phase 3: Present Findings

After the agent completes, present to the user:

1. **Verdict** — READY / NEEDS CLARIFICATION / NOT TESTABLE
2. **Ambiguities found** — list each one
3. **Questions to resolve** — list each one
4. **Missing edge cases** — list each one

If verdict is READY:
> Requirement is ready. Run `/design_tests <slug>` to begin test design.

If verdict is NEEDS CLARIFICATION:
> Please answer the questions above before proceeding to design.

If verdict is NOT TESTABLE:
> This requirement cannot be automated as stated. Reason: <explanation>
