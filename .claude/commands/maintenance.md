# Maintain Tests Command

You are coordinating test suite updates after changes to the web application under test.

**Core principle:** Preserve test intent. Only update what broke — nothing more.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — app name (`the_internet`)
- `$ARGUMENTS[1+]` — description of what changed in the application

If no description provided, ask:
> What changed in the application? Describe the change as specifically as possible.
> Examples:
> - "The login button text changed from 'Login' to 'Sign In'"
> - "The error message selector changed from `.error` to `[data-test=error]`"
> - "The /drag_and_drop URL path changed to /drag-and-drop"

---

## Phase 2: Research Impact

Spawn the `codebase-explorer` subagent (Agent tool with `subagent_type: "codebase-explorer"`):

Ask it to:
- Find all page objects for the specified app
- Find all locator constants for the specified app
- Find all test files for the specified app
- Identify which files reference the changed element (by selector, text, or URL)

Wait for research to complete.

---

## Phase 3: Assess and Confirm

Present the impacted files to the user:

```
Change: <description>

Affected files:
- <file>:<line> — <what references the changed element>

Proposed updates:
- <file>:<line>: change `<old>` to `<new>`

Proceed?
```

Wait for confirmation before making any changes.

---

## Phase 4: Apply Updates

Spawn the `maintainer` subagent (Agent tool with `subagent_type: "maintainer"`):

Pass:
- The change description
- The list of affected files from research
- The proposed updates
- Instruction to save report to `thoughts/maintenance/YYYY-MM-DD-<slug>.md`

Wait for completion.

---

## Phase 5: Verify

After maintainer completes, run the affected tests:

```bash
pytest tests/<app>/ -v --no-header --tb=short
```

If tests pass:
> Maintenance complete. All affected tests pass.
> Changes saved to: thoughts/maintenance/YYYY-MM-DD-<slug>.md

If tests still fail:
> Some tests are still failing after the update.
> Run `/debug_tests <app>` to diagnose the remaining failures.
