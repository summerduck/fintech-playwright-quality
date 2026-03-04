# Debug Tests Command

You are coordinating the diagnosis of failing E2E tests.

**Core principle:** Run first, diagnose second. Never guess — read the actual code.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — scope: test file path, node ID, marker name, or app name
  - Examples: `tests/the_internet/test_login.py`, `the_internet`, `smoke`
- `$ARGUMENTS[1]` — (optional) specific test node ID to target

If no arguments provided, ask:
> What tests should I run? Provide a file path, app name, or pytest marker.

---

## Phase 2: Run the Tests

Run pytest with the provided scope:

```bash
# By file
pytest <file_path> -v --no-header --tb=short

# By app directory
pytest tests/<app>/ -v --no-header --tb=short

# By marker
pytest -m <marker> -v --no-header --tb=short

# By node ID
pytest <node_id> -v --no-header --tb=short
```

Capture the full output.

---

## Phase 3: Triage Results

If all tests pass:
> All tests passed. No debugging needed.
> Run `/reporting` to get a full report.

If tests fail, for each failure:
- Extract: test node ID, exception type, error message, traceback

---

## Phase 4: Spawn Bug Tracer

For each failing test, spawn a `bug-tracer` subagent (Agent tool with `subagent_type: "bug-tracer"`):

Pass:
- The full failure output for that test
- The test node ID
- Instruction to save diagnosis to `thoughts/debug/YYYY-MM-DD-<slug>.md`

Run up to 3 bug-tracer tasks in parallel (one per failing test). Run sequentially if more than 3 failures.

Wait for all agents to complete.

---

## Phase 5: Present Diagnosis

For each diagnosed failure, present:

```
Test: <node ID>
Category: <SELECTOR | TIMING | LOGIC | FIXTURE | ...>
Root cause: <file>:<line> — <description>
Fix: <plain English instruction>
Confidence: HIGH | MEDIUM | LOW
```

Then ask:
> Should I proceed with fixes? (Yes = spawn implement agent with the fix instructions)
> Or do you want to fix manually?

---

## Phase 6: Apply Fixes (if approved)

If user approves:
1. Spawn `implement` subagent with the fix instructions from each diagnosis.
2. After fixes, re-run the same pytest command.
3. If all pass → show summary.
4. If still failing → re-run diagnosis (max 1 retry cycle).
