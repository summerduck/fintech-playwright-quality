# Apply Fixes Command

You are coordinating the application of fixes diagnosed by the `bug-tracer` agent.

**Core principle:** Only fix what is diagnosed — read the report before touching any file.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — scope that was passed to `/debug` (app name, file path, marker, or test node ID)

If no scope provided, ask:
> What scope was passed to `/debug`? (e.g. `acceptapayment`, `tests/accept_a_payment/test_card.py`, `smoke`)

---

## Phase 2: Read Debug Report

Find the most recent debug report matching the scope:

```
thoughts/debug/YYYY-MM-DD-<slug>.md
```

If no report is found, stop and tell the user:
> No debug report found for scope `<scope>`. Run `/debug <scope>` first.

Read the report completely. Extract for each diagnosed failure:
- Test node ID
- Category (`SELECTOR` | `TIMING` | `LOGIC` | `FIXTURE` | `ASSERTION` | `IMPORT` | `CONFIG` | `FLAKY` | `ENVIRONMENT`)
- File and line to change
- Fix instruction (plain English)
- Confidence level

Skip any failure with `status: INCONCLUSIVE` or confidence `LOW` — report these to the user and ask whether to skip or attempt anyway.

---

## Phase 3: Present Fix Plan

Before applying anything, show the user what will be changed:

```
Fixes to apply:

1. Test: <node ID>
   Category: <CATEGORY>
   File: <path>:<line>
   Fix: <description>
   Confidence: HIGH | MEDIUM

(Skipped — INCONCLUSIVE:)
- <node ID>: <reason>
```

Ask:
> Proceed with applying these fixes?

Wait for confirmation before continuing.

---

## Phase 4: Apply Fixes

For each fix (up to 3 in parallel if independent files; sequential if same file):

Spawn an `implement` subagent (Agent tool with `subagent_type: "implement"`):

Pass:
- The fix instruction from the debug report
- The exact file and line to change
- The category (to guide the type of change)
- Instruction: apply only the described fix — do not refactor surrounding code

Wait for the subagent to complete.

---

## Phase 5: Verify Fixes

After all fixes are applied, run the previously failing tests:

```bash
pytest <node IDs of fixed tests> -v --no-header --tb=short
```

Run each fixed test individually. For each:

- **PASS** — fix confirmed
- **FAIL** — fix did not resolve the issue; report the new output

---

## Phase 6: Report Results

Present a summary:

```
Fix Summary

Applied:
- [PASS] <node ID> — <file>:<line> fixed
- [FAIL] <node ID> — still failing after fix (see output below)

Skipped:
- <node ID> — INCONCLUSIVE / LOW confidence

Remaining failures:
<paste test output for still-failing tests>
```

If all fixes pass:
> All diagnosed failures resolved. Run `/open_pr` when ready to commit.

If any fixes fail:
> <N> failure(s) remain. Run `/debug <scope>` to re-diagnose with the new output.
