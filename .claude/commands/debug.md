# Debug Command

You are coordinating the diagnosis and fixing of failing E2E tests.

**Core principle:** Never guess — read the actual output and code before diagnosing anything.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — pytest output: pasted text, file path to output, or path to a saved log file

If no output is provided, ask:
> Please paste the pytest output or provide a path to the saved log file.

If a file path is provided, read it completely before proceeding.

---

## Phase 2: Triage Results

Parse the output:

If all tests passed:
> All tests passed. No debugging needed.
> Run `/reporting` to get a full report.

If tests failed, for each failure extract:
- Test node ID
- Exception type
- Error message
- Traceback

---

## Phase 3: Spawn Bug Tracer

For each failing test, spawn a `bug-tracer` subagent (Agent tool with `subagent_type: "bug-tracer"`):

Pass:
- The full failure output for that test
- The test node ID
- Instruction to save diagnosis to `thoughts/debug/YYYY-MM-DD-<slug>.md`

Run up to 3 bug-tracer tasks in parallel (one per failing test). Run sequentially if more than 3 failures.

Wait for all agents to complete.

---

## Phase 4: Present Diagnosis

For each diagnosed failure, present:

```
Test: <node ID>
Category: <SELECTOR | TIMING | LOGIC | FIXTURE | ...>
Root cause: <file>:<line> — <description>
Fix: <plain English instruction>
Confidence: HIGH | MEDIUM | LOW
```

Then say:
> Run `/apply_fixes <scope>` to apply these fixes automatically, or fix manually.
