# Debug Command

You are coordinating the diagnosis and fixing of failing E2E tests.

**Core principle:** Never guess — read the actual output and code before diagnosing anything.

---

## Phase 1: Resolve Output

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` *(optional)* — pasted pytest output, or explicit path to a specific file

**If no argument is provided:** collect data from all known output locations:

| Location | What it contains |
|----------|-----------------|
| `thoughts/runs/*.txt` | raw pytest output saved by `/run_tests` |
| `test-logs/*.log` | per-test worker logs (pytest-xdist) |
| `test-results/failed_tests/` | Playwright trace/screenshot for failed tests |
| `report.html` | pytest-html report (parse for FAILED rows) |
| `allure-results/` | Allure JSON results (parse `*-result.json` for `status: failed`) |

Read every source that exists. Aggregate all failures across all sources. Tell the user what was loaded:

> Found test data in:
> - `thoughts/runs/` — N file(s)
> - `test-logs/` — N log(s)
> - `report.html` — N failures
> - `allure-results/` — N failed result(s)
> Diagnosing N unique failing tests.

De-duplicate failures by test node ID — if the same test appears in multiple sources, merge the information and use the most detailed failure output available.

**If a file path is provided:** read only that file.

**If raw text is pasted:** use it directly.

If none of the above locations contain any data, ask:
> No test output found. Run `/run_tests <scope>` first, or paste the pytest output here.

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
