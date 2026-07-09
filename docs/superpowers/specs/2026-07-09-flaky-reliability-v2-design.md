# Flaky Reliability v2 — Quarantine, Flake History, Auto-Detection

**Date:** 2026-07-09
**Status:** Approved
**Builds on:** v1 (PR #56/#57) — CI-only infra-shaped retries via pytest-rerunfailures,
loud pass-on-retry summary (`utils/flaky_summary.py`).

## Goal

Close the flaky-test lifecycle. v1 detects single-run flakes (pass-on-retry) and
reports them loudly. v2 adds the remaining stages:

- **Contain**: a quarantine mechanism so a known-flaky test stops blocking merges
  while still running and producing signal.
- **Remember**: durable per-test flake history across CI runs.
- **Decide**: threshold-based detection that proposes quarantine and
  un-quarantine candidates. A human applies every change via a reviewed PR.

## Decisions (with rationale)

| Decision | Choice |
|---|---|
| Quarantine semantics | Run, but never block: `quarantine` marker → `xfail(strict=False)`. Failures become XFAIL, passes become XPASS. Industry consensus (Google, Dropbox, Trunk, Datadog); pytest docs endorse non-strict xfail as "a manual quarantine". |
| Storage | `flake-history/history.json` on the `gh-pages` branch, written only by the existing `publish-report` job (already the single gh-pages writer for Allure history). Permanent, auditable via git log, zero new concurrency surface. |
| Automation level | Detect and propose only. CI emits a candidates report; a human adds/removes markers in a reviewed PR. No bot ever changes test code or a quarantine list. |
| Detection thresholds | Quarantine candidate: ≥2 flake incidents within the last 30 recorded runs, OR fail rate ≥5% over ≥10 runs. A flake incident = pass-on-retry (same-commit fail+pass, `reruns > 0` and final pass). |
| Release thresholds | Un-quarantine candidate: 10 consecutive clean runs. For a quarantined test, clean = XPASS (it ran, passed, and no longer needed the quarantine shield). |
| Marker hygiene | Every `quarantine` marker requires `reason` and `expires` (ISO date, ~30 days out). An expired marker aborts the run with `UsageError` naming the test — forces fix-or-extend, never silent decay. |
| Plugins | Keep pytest-rerunfailures (healthy, pytest-dev). Do NOT adopt pytest-quarantine (abandoned since 2020). Build small custom conftest plugins, consistent with v1. |

## Architecture

Three new units, each single-purpose, following v1's pattern of small pytest
plugins registered from the root `conftest.py` via `pytest_plugins`:

### 1. `utils/quarantine.py` — quarantine marker plugin

- Registers marker: `quarantine(reason: str, expires: str)`.
- `pytest_collection_modifyitems`: for each quarantined item
  - `expires` in the past → collect into an error list; after the loop raise
    `pytest.UsageError` listing every expired quarantine (test id, reason, date).
  - otherwise → `item.add_marker(pytest.mark.xfail(reason=..., strict=False))`.
- Side effect worth noting: pytest-rerunfailures does not rerun xfailed tests,
  so quarantined tests stop consuming CI retry budget.

### 2. `utils/run_record.py` — per-run outcome recorder

- Records every test's final outcome for the run: `nodeid`, outcome
  (`passed | failed | xfailed | xpassed | skipped`), `reruns` used,
  `quarantined` flag.
- xdist-aware exactly like `utils/flaky_summary.py`: workers forward reports,
  only the controller writes (guard on `workerinput`).
- Writes `test-logs/run-records/run-record-<browser>.json` at session end.
  `test-logs/` is already volume-mounted in docker compose and uploaded as the
  `test-artifacts-<browser>` artifact — no new CI upload steps.
- Inert unless `GITHUB_RUN_ID` is set (CI-only, like v1 retries): local runs
  write nothing. The tests run inside docker compose, which does not inherit
  runner env — the workflow's `docker compose run` command must pass
  `-e GITHUB_RUN_ID -e GITHUB_SHA -e GITHUB_REF_NAME` (same bridging v1 needed
  for `GITHUB_STEP_SUMMARY`).

### 3. `scripts/analyze_flake_history.py` — history merge + threshold analysis

Runs inside the existing `publish-report` job (main-branch pushes only), which
already checks out gh-pages and downloads all browser artifacts:

1. Load `gh-pages/flake-history/history.json` (or start fresh).
2. Merge the run-record JSONs from all browser jobs into history, keyed by
   `(nodeid, browser)`, windowed to the last 50 runs per key.
3. Apply thresholds → two candidate lists (quarantine / un-quarantine).
4. Write updated `history.json` + `candidates.md` into the publish tree
   (deployed to gh-pages next to the Allure report) and append the candidates
   report to `$GITHUB_STEP_SUMMARY`.

The analyzer proposes; it never edits test code, never fails the build.

## Data formats

Run record (one per browser job per run):

```json
{
  "schema": 1,
  "run_id": "123456789",
  "sha": "abc1234",
  "branch": "main",
  "browser": "chromium",
  "timestamp": "2026-07-09T12:00:00Z",
  "tests": [
    {"nodeid": "tests/x/test_y.py::test_z", "outcome": "passed", "reruns": 1, "quarantined": false}
  ]
}
```

History (gh-pages, single file):

```json
{
  "schema": 1,
  "tests": {
    "tests/x/test_y.py::test_z": {
      "chromium": [
        {"run_id": "123456789", "sha": "abc1234", "outcome": "passed", "reruns": 1}
      ]
    }
  }
}
```

- History accrues from main-branch runs only (the publish job's existing
  `if: github.ref == 'refs/heads/main'` guard) — PR runs never pollute stats.
- `timestamp` is stamped once by the recorder plugin at session end (UTC) —
  run metadata, not test data; individual test entries carry no timestamps.

## Data flow

```
browser job (×3 on main)             publish-report job (main only, single writer)
────────────────────────             ─────────────────────────────────────────────
pytest run                           download artifacts (allure + test-logs, ×3)
 ├─ quarantine.py: marker→xfail      checkout gh-pages (existing step)
 ├─ run_record.py: outcomes ──┐      analyze_flake_history.py:
 └─ upload test-logs artifact ┴──►     history.json ⊕ run records → history.json'
                                       thresholds → candidates.md
                                     step summary + deploy to gh-pages (existing)
```

## Detection rules (analyzer)

Per `(nodeid, browser)` key over its recorded window:

- **Flake incident**: a run with `reruns > 0` and final outcome `passed`
  (v1's pass-on-retry — same commit failed then passed).
- **Quarantine candidate**: not currently quarantined AND
  (≥2 flake incidents in the last 30 runs, OR
  fail rate ≥5% with ≥10 recorded runs).
- **Un-quarantine candidate**: currently quarantined AND the 10 most recent
  runs are all `xpassed` with `reruns == 0`.
- A test currently failing deterministically (fail streak, no passes) is
  reported as "failing, not flaky" — quarantine is for flakes, not regressions.

## Error handling

- Corrupt or schema-mismatched `history.json` → warn, start fresh history.
  History is derived data; the git log of gh-pages retains old versions.
- Missing run-record artifact (browser job died before writing) → analyze
  what exists; list the gap in `candidates.md`.
- The analyze step uses `continue-on-error: true` in the workflow so a bug in
  analysis is loud in the run log but never blocks Allure publishing.
- Expired quarantine markers are the one deliberate hard failure
  (`UsageError` at collection) — by design, in the test job, not the analyzer.

## Testing

- `tests/framework/test_quarantine.py` (pytester): marker→xfail conversion;
  quarantined failure does not fail the run; XPASS recorded; expired marker
  aborts with the expected message; missing `reason`/`expires` rejected.
- `tests/framework/test_run_record.py` (pytester): record file written with
  correct outcomes/reruns; nothing written without `GITHUB_RUN_ID`; xdist
  controller-only writing.
- `tests/framework/test_flake_analysis.py` (plain unit tests): threshold
  functions over in-memory history fixtures — candidate/no-candidate cases,
  windowing, fail-rate edge cases, deterministic-failure exclusion,
  corrupt-history recovery.
- A `quarantine`-marked demo test (analogous to `flaky_demo`) proving the
  end-to-end pipeline in CI.

## Out of scope (YAGNI)

- Auto-opening PRs or issues for candidates.
- Cross-repo or external flaky-test services (BuildPulse, Trunk, Datadog).
- Quarantine list files outside test code — the marker in the test file IS the
  quarantine list; `git grep quarantine` enumerates it.
- Per-test flake dashboards beyond `candidates.md` + Allure trends.

## Sources

- GitHub: Reducing flaky builds by 18x — same-commit pass+fail definition.
- Google Testing Blog: Flaky Tests at Google — quarantine + keep-running.
- pytest docs (explanation/flaky) — non-strict xfail as manual quarantine.
- Datadog Flaky Tests Management — threshold/30-day auto-fix policies.
- Testim — flaky→normal after 10 consecutive passes.
- pytest-quarantine (PyPI/Snyk) — inactive since 2020; informed marker design.
