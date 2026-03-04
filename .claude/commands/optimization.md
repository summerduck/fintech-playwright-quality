# Optimize Tests Command

You are coordinating a health check of the test suite.

**Core principle:** Find what is slowing, breaking, or cluttering the suite — surface it clearly so the team can decide what to fix.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — scope: `all`, app name (`the_internet`, `saucedemo`, `uiplayground`), or `quick` (static analysis only, no test run)
- Default scope if omitted: `all`

---

## Phase 2: Run Tests with Timing (unless `quick`)

If scope is not `quick`, run the full suite for the scope:

```bash
# All tests with durations
pytest tests/ -v --no-header --tb=no --durations=10

# By app
pytest tests/<app>/ -v --no-header --tb=no --durations=10
```

Capture the full output including per-test durations.

---

## Phase 3: Spawn Optimizer

Spawn the `optimizer` subagent (Agent tool with `subagent_type: "optimizer"`):

Pass:
- Pytest output with durations (or empty if `quick` mode)
- Scope description
- Instruction to analyze all test and page object files in scope
- Instruction to save to `thoughts/optimization/YYYY-MM-DD-<scope>.md`

Wait for the agent to complete.

---

## Phase 4: Present Findings

After the agent completes, present findings grouped by priority:

```
Optimization Report — <scope> — <date>

HIGH (reliability):
- <issue> in <file>:<line>

MEDIUM (performance):
- <issue> in <file>:<line>

LOW (cleanup):
- <issue> in <file>:<line>

Coverage gaps:
- <gap>

Full report: thoughts/optimization/YYYY-MM-DD-<scope>.md
```

Then ask:
> Which issues would you like to fix?
> - Fix reliability issues (flaky patterns)
> - Fix performance issues (slow tests)
> - Clean up dead code
> - All of the above

Based on the answer, spawn the `maintainer` subagent to apply the selected fixes, or hand off to the user with the report.
