# Flaky Reliability: Deterministic Retry Policy — Design

**Date:** 2026-07-06
**Status:** Approved for planning

## Goal

Introduce a deliberate, bounded, visible retry policy for e2e tests so that
flaky behavior is *detected and surfaced* rather than silently masked.
Pass-on-retry is counted separately from clean pass. One intentionally
(deterministically) flaky demo test proves the pipeline end to end.
Quarantine and history-based auto-detection are roadmap items only.

## Guiding principle

Retries are an observability mechanism, not a fix. This reconciles the
feature with the project rule "handle flaky tests by improving selectors or
wait conditions, not by adding retries": assertion failures never retry
(a wrong answer twice is still a wrong answer), only infrastructure-shaped
failures (timeouts, network errors) are retry-eligible, and every retry is
loudly reported.

## Decisions (locked)

| Decision | Choice |
|---|---|
| Retry scope | CI-only, browser-e2e-only, max 1 retry. Local and unit-test runs keep `--reruns=0`. API tests (planned next) are never retry-eligible. |
| Retry eligibility | Only infra-shaped failures via `--only-rerun` regex; assertion failures never retry. |
| Flaky counting | Custom `pytest_terminal_summary` hook prints `flaky (passed on retry): N` + test list, distinct from clean passes. Allure Retries tab provides report-side visibility for free. |
| Demo test | Runs in every CI run so the published Allure report always demonstrates retry marking. |
| Quarantine / auto-detection | README roadmap entry only. No implementation. |

## Architecture

### 1. Retry policy (CI workflow)

`.github/workflows/tests.yml`, "Run tests" step:

```
docker compose run --rm tests --browser=${{ matrix.browser }} \
  --reruns=1 --only-rerun "TimeoutError|net::ERR"
```

- Args appended after the service name pass straight through to pytest in
  the runner container (same mechanism as `--browser`).
- pytest CLI args take precedence over `addopts`, so `--reruns=1` overrides
  the `--reruns=0` default in `pyproject.toml` with no config change.
- `--only-rerun` matches against the failure repr: Playwright
  `TimeoutError` and Chromium network errors (`net::ERR_*`) are eligible;
  `AssertionError` is not.
- `pyproject.toml` keeps `--reruns=0` with a short comment block explaining
  the policy and pointing at the workflow.

Retry eligibility is a property of the test layer, not the run: only
browser-driven e2e tests may retry, because only they fail on browser/infra
noise. API tests (planned as the next suite) must never retry — an HTTP
timeout against the app under test is signal, not noise, and the
`--only-rerun` regex alone cannot exclude them (`requests` timeout
tracebacks contain `ConnectTimeoutError`/`ReadTimeoutError`, which would
match `TimeoutError`). Mechanism, binding when `tests/api/` is created:
its `conftest.py` carries a `pytest_collection_modifyitems` hook stamping
`pytest.mark.flaky(reruns=0)` on every collected item — per-test flaky
markers take precedence over the CLI `--reruns` flag in
pytest-rerunfailures, so the API suite opts itself out regardless of how
CI invokes pytest. Same pattern applies to any future non-browser layer.
No code ships for this now (the directory does not exist yet).

### 2. Flaky-count terminal hook (root `conftest.py`)

~20 lines:

- `pytest_runtest_logreport` records nodeids whose report outcome is
  `"rerun"` (emitted by pytest-rerunfailures for each failed attempt) and
  nodeids that ultimately passed.
- `pytest_terminal_summary` prints a distinct section:
  `flaky (passed on retry): N` with the offending nodeids, and
  `failed after retry` for tests that were retried and still failed.
- Works under xdist: reports are forwarded to the controller, where the
  terminal summary runs.
- Unit-tested in `tests/framework/test_flaky_summary.py` using `pytester`
  (subprocess runs with `--reruns` enabled to simulate retries; no live
  browser needed).

### 3. Deterministic flaky demo test

`tests/accept_a_payment/test_flaky_demo.py`:

- Marked `@pytest.mark.flaky_demo` (registered in `pyproject.toml`
  markers — `--strict-markers` is on).
- Deterministic behavior: fails on attempt 1, passes on attempt 2, keyed on
  `request.node.execution_count` (set by pytest-rerunfailures; starts
  at 1). Never uses randomness — the flake reproduces 100% of the time.
- The attempt-1 failure raises Playwright `TimeoutError` so it matches the
  `--only-rerun` regex and is retry-eligible.
- Project rule "no Python logic in test bodies" applies: the
  attempt-counting conditional lives in a fixture (`flaky_simulation`) in
  the e2e `conftest.py`, not in the test body. The test itself is a flat
  call sequence.
- When retries are disabled (`--reruns=0`, i.e. every local run), the
  fixture skips the test with an explanatory reason instead of hard-failing.
- Allure title/description make its intent unmistakable in the published
  report.

### 4. Documentation

- README: short "Flaky reliability" subsection (policy, what pass-on-retry
  means, link to a sample report) + roadmap row
  "Flaky quarantine & auto-detection — Planned" (history-based detection,
  auto-quarantine marker, feeds the planned Failure Triage Agent).

## Error handling

- Demo test under `--reruns=0`: skip with reason, never a hard local failure.
- Retried-and-still-failed tests: reported in their own summary bucket;
  they are failures, not flakes.
- Hook is inert when rerunfailures is disabled (e.g. mutmut profile uses
  `-p no:rerunfailures`): no `rerun` reports means no flaky section.

## Testing

- `tests/framework/test_flaky_summary.py` (pytester): clean pass shows no
  flaky section; fail-then-pass shows `flaky (passed on retry): 1`;
  fail-then-fail lands in `failed after retry`.
- Demo test itself is the e2e proof: every CI run on main publishes an
  Allure report containing one flaky-marked test with a visible retry.

## Out of scope

- Quarantine mechanism, flake-history storage, auto-detection thresholds.
- Any change to unit-test or local retry behavior.
- Failure Triage Agent integration (separate roadmap phase).
- The `tests/api/` opt-out hook itself — specified above, implemented with
  the API suite.
