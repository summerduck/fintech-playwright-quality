# CI Execution Command

You are coordinating the monitoring and diagnosis of CI pipeline results.

**Core principle:** Read the actual CI output before drawing any conclusions. Never guess at environment-specific failures.

---

## Phase 1: Parse Arguments

Arguments: `$ARGUMENTS`

- `$ARGUMENTS[0]` — (optional) PR number, branch name, or run ID
  - Examples: `123`, `feature/login-tests`, `9876543210`
- If omitted, use the current branch's most recent run

---

## Phase 2: Fetch CI Status

Get the current branch if no argument provided:

```bash
git branch --show-current
```

Fetch the latest CI run:

```bash
# By PR number
gh pr checks <pr-number>

# By branch (most recent run)
gh run list --branch <branch> --limit 5

# By run ID
gh run view <run-id>
```

Present the pipeline status:

```
CI Run — <branch> — <run ID>

Status: PASSED | FAILED | IN PROGRESS
Jobs:
  ✓ lint
  ✗ test (2 failures)
  ✓ type-check
```

If the pipeline is still running:
> CI is still in progress. Re-run `/ci` once it completes.

---

## Phase 3: Triage Results

If all jobs passed:
> CI passed. No action needed.
> The branch is ready to merge.

If jobs failed, fetch the full log for each failing job:

```bash
gh run view <run-id> --log-failed
```

For each failure, extract:
- Job name
- Step name
- Error message and stack trace

---

## Phase 4: Classify Failures

Classify each failure as one of:

| Category | Description |
|----------|-------------|
| `ENVIRONMENT` | Missing env var, wrong Python version, missing dependency |
| `IMPORT` | Module not found, path issue specific to CI |
| `SELECTOR` | Element not found — possibly due to headless rendering |
| `TIMING` | Timeout — CI machines are slower than local |
| `CONFIG` | Wrong base URL, wrong browser, missing playwright install |
| `TEST_LOGIC` | Genuine test failure, not environment-related |
| `FLAKY` | Passed on retry or failed non-deterministically |

Present each classified failure:

```
Job: <job name>
Step: <step name>
Category: <category>
Error: <message>
Likely cause: <plain English>
Fix: <specific instruction>
```

---

## Phase 5: Recommend Action

Based on the classification:

- `ENVIRONMENT` / `IMPORT` / `CONFIG` → fixes go in config files (`.github/workflows/`, `pyproject.toml`, `conftest.py`)
- `SELECTOR` / `TIMING` → fixes go in page objects or test files; run `/run_and_debug` locally first
- `TEST_LOGIC` → genuine failure; run `/run_and_debug <scope>` to investigate
- `FLAKY` → note it; run `/optimization` to address flakiness

Ask the user:
> Should I apply the environment/config fixes, or will you handle them manually?

---

## Phase 6: Apply Fixes (if approved)

If user approves:
1. Apply config-level fixes directly (edit workflow files, pyproject.toml, etc.)
2. For test-level fixes, spawn `implement` subagent with the fix instructions.
3. After fixes are applied, confirm:
   > Changes made. Push to trigger a new CI run, then re-run `/ci` to verify.
