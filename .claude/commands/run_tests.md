# Run Tests Command

You are running the test suite for a given scope and producing output ready for debugging if needed.

**Core principle:** Run, record, report — do not fix anything.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — scope: app name, test file path, marker, or test node ID

If no scope provided, ask:
> What scope should I run? Examples:
> - App: `acceptapayment`
> - File: `tests/accept_a_payment/test_card.py`
> - Marker: `smoke`
> - Node ID: `tests/accept_a_payment/test_card.py::TestPageLoadAndInitialState::test_page_title_is_card`

---

## Phase 2: Run Tests

Spawn a `test-runner` subagent (Agent tool with `subagent_type: "test-runner"`):

Pass:
- The scope to run
- Instruction to skip the pre-run gate checks (plan.md / review.md) — this is a standalone run, not part of an implement phase
- Instruction to run:

```bash
pytest <scope> -v --no-header --tb=short
```

Where `<scope>` maps to:
- App name → `tests/<app>/`
- File path → pass as-is
- Marker → `-m <marker>`
- Node ID → pass as-is

Wait for the subagent to complete.

---

## Phase 3: Report Results

Present the full test output to the user.

If all tests passed:
> All tests passed.
> Run `/reporting <scope>` for a full structured report.

If tests failed or errored:
> <N> test(s) failed. Run `/debug` to diagnose the failures (picks up this run automatically).

Save the raw pytest output to `thoughts/runs/YYYY-MM-DD-<scope-slug>.txt`.
