# Report Tests Command

You are coordinating the generation of a test suite report.

**Core principle:** Run the tests, parse the output, surface what matters.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — scope: `all`, app name (`the_internet`, `saucedemo`, `uiplayground`), or marker (`smoke`, `regression`)
- Default scope if omitted: `all`

---

## Phase 2: Run the Tests

Run pytest for the given scope:

```bash
# All tests
pytest tests/ -v --no-header --tb=line

# By app
pytest tests/<app>/ -v --no-header --tb=line

# By marker
pytest -m <marker> -v --no-header --tb=line
```

Capture the full output including durations (`--tb=line` keeps output concise).

---

## Phase 3: Spawn Reporter

Spawn the `reporter` subagent (Agent tool with `subagent_type: "reporter"`):

Pass:
- Full pytest output
- Scope description
- List of all test files in scope (from Glob)
- Instruction to save to `thoughts/reports/YYYY-MM-DD-<scope>.md`

Wait for the agent to complete.

---

## Phase 4: Present Report

After the agent completes, present a summary to the user:

```
Test Report — <scope> — <date>

Status: ALL PASSED | N FAILURES
Pass rate: N%
Total: N tests in Ns

Failed: (list if any)
Slowest: (top 3)
Coverage gaps: (list if any)

Full report saved to: thoughts/reports/YYYY-MM-DD-<scope>.md
```

If there are failures:
> Run `/debug_tests <scope>` to diagnose the failures.

If there are coverage gaps:
> Run `/design_tests <feature>` to add missing tests.
