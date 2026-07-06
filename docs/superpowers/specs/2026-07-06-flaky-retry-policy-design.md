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
| Retry scope | CI-only, browser-e2e-only, max 1 retry. Local and unit-test runs keep `--reruns=0`. The existing `tests/framework/` suite opts out now; API tests (planned next) are never retry-eligible. |
| Retry eligibility | Only infra-shaped failures via `--only-rerun` regex, covering all three matrix browsers (Chromium `net::ERR_*`, Firefox `NS_ERROR_*`, WebKit's freeform "Could not connect"); assertion failures never retry. |
| Flaky counting | Custom `pytest_terminal_summary` hook prints `flaky (passed on retry): N` + test list, distinct from clean passes, and mirrors the section to `$GITHUB_STEP_SUMMARY`. The demo test is bucketed on its own `flaky (demo)` line so the real flake count starts at 0. Allure Retries tab provides report-side visibility for free. |
| Demo test | Lives in `tests/framework/`, runs in every CI run so the published Allure report always demonstrates retry marking. Counted separately (see above). |
| Quarantine / auto-detection | README roadmap entry only. No implementation. |

## Architecture

### 1. Retry policy (CI workflow)

`.github/workflows/tests.yml`, "Run tests" step:

```
docker compose run --rm tests --browser=${{ matrix.browser }} \
  --reruns=1 --only-rerun "TimeoutError|net::ERR|NS_ERROR_|Could not connect"
```

- Args appended after the service name pass straight through to pytest in
  the runner container (same mechanism as `--browser`).
- pytest CLI args take precedence over `addopts`, so `--reruns=1` overrides
  the `--reruns=0` default in `pyproject.toml` with no config change.
- `--only-rerun` matches against the failure repr. The regex covers all
  three browsers in the main-branch matrix: Playwright `TimeoutError`
  (all browsers), Chromium network errors (`net::ERR_*`), Firefox network
  errors (`NS_ERROR_*`), and WebKit's freeform network messages
  ("Could not connect ..."). `AssertionError` is not eligible.
- Accepted over-match risk: the `Could not connect` fragment (and, less
  plausibly, `TimeoutError`) could appear inside captured page text of a
  genuine assertion failure, making it retry-eligible. A deterministic
  wrong answer still fails on the retry, and the max-1-retry bound caps
  the cost, so this is accepted rather than tightened — anchoring the
  regex to qualified exception names risks false negatives because
  pytest's rendering of exception names varies with traceback style.
- Known cost: a genuinely broken selector now fails with a
  `TimeoutError`, retries, and waits out the full Playwright timeout a
  second time — time-to-red roughly doubles for timeout-shaped real
  failures on each matrix leg. Accepted at max 1 retry.
- `pyproject.toml` keeps `--reruns=0` with a short comment block explaining
  the policy and pointing at the workflow.

Retry eligibility is a property of the test layer, not the run: only
browser-driven e2e tests may retry, because only they fail on browser/infra
noise. The CI invocation, however, scopes by run — `docker compose run
tests` collects the whole `tests/` tree — so every non-e2e layer must
carry an explicit opt-out or it silently inherits `--reruns=1`. The
mechanism, per layer: the layer's `conftest.py` carries a
`pytest_collection_modifyitems` hook stamping `pytest.mark.flaky(reruns=0)`
on every collected item — per-test flaky markers take precedence over the
CLI `--reruns` flag in pytest-rerunfailures, so the layer opts itself out
regardless of how CI invokes pytest.

Applied now, in scope: `tests/framework/conftest.py` stamps the opt-out on
every item **except** those carrying the `flaky_demo` marker (the demo
test must stay retry-eligible — see §3). Without this, the framework unit
suite — including the flaky-summary test itself — would be retry-eligible
from day one.

Applied later, binding when `tests/api/` is created: same hook, no
exemption. API tests must never retry — an HTTP timeout against the app
under test is signal, not noise, and the `--only-rerun` regex alone cannot
exclude them (`requests` timeout tracebacks contain
`ConnectTimeoutError`/`ReadTimeoutError`, which would match
`TimeoutError`). Same pattern applies to any future non-browser layer.
No API code ships now (the directory does not exist yet).

### 2. Flaky-count terminal hook (root `conftest.py`)

~25 lines:

- `pytest_runtest_logreport` records nodeids whose report outcome is
  `"rerun"` (emitted by pytest-rerunfailures for each failed attempt) and
  nodeids that ultimately passed.
- `pytest_terminal_summary` prints a distinct section:
  `flaky (passed on retry): N` with the offending nodeids, and
  `failed after retry` for tests that were retried and still failed.
- Tests carrying the `flaky_demo` marker are bucketed onto a separate
  `flaky (demo): N` line, never counted in the real flaky total. The
  demo runs in every CI run, so folding it into the main count would
  set a permanent baseline of 1 per matrix leg and the first genuine
  flake would surface as a `1 → 2` delta — exactly the kind of change
  that gets missed. With the separate line, any nonzero real count is
  unambiguous signal.
- When `$GITHUB_STEP_SUMMARY` is set (CI), the hook appends the same
  section there, so flaky counts are visible on the Actions run page
  without opening logs — retries are meant to be loud.
- Works under xdist: reports are forwarded to the controller, where the
  terminal summary runs. This is not assumed — xdist is the default
  execution mode (`-n=auto` in `addopts`), so the pytester suite includes
  an explicit `-n 2` case (see Testing).
- Unit-tested in `tests/framework/test_flaky_summary.py` using `pytester`
  (subprocess runs with `--reruns` enabled to simulate retries; no live
  browser needed).

### 3. Deterministic flaky demo test

`tests/framework/test_flaky_demo.py`:

- Lives in `tests/framework/`, not a feature suite: it exercises retry
  infrastructure, touches no page object or browser, and must not inflate
  the payment suite's test counts or coverage picture. Its `flaky_demo`
  marker exempts it from the framework layer's `reruns=0` stamp (§1).
- Marked `@pytest.mark.flaky_demo` (registered in `pyproject.toml`
  markers — `--strict-markers` is on).
- Deterministic behavior: fails on attempt 1, passes on attempt 2, keyed on
  `request.node.execution_count` (set by pytest-rerunfailures; starts
  at 1). The fixture reads it as
  `getattr(request.node, "execution_count", 1)` — the attribute does not
  exist when the plugin is disabled outright (mutmut profile runs
  `-p no:rerunfailures`). Never uses randomness — the flake reproduces
  100% of the time.
- The attempt-1 failure raises Playwright `TimeoutError` so it matches the
  `--only-rerun` regex and is retry-eligible.
- Project rule "no Python logic in test bodies" applies: the
  attempt-counting conditional lives in a fixture (`flaky_simulation`) in
  `tests/framework/conftest.py`, not in the test body. The test itself is
  a flat call sequence.
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
  `-p no:rerunfailures`): no `rerun` reports means no flaky section. In
  that mode `request.node.execution_count` also does not exist — the demo
  fixture's `getattr(..., 1)` default keeps it from raising
  `AttributeError` (it then skips via the `--reruns=0` path).
- Time-to-red on real timeout-shaped failures doubles per matrix leg
  (accepted; see §1).

## Testing

- `tests/framework/test_flaky_summary.py` (pytester): clean pass shows no
  flaky section; fail-then-pass shows `flaky (passed on retry): 1`;
  fail-then-fail lands in `failed after retry`; a `flaky_demo`-marked
  fail-then-pass lands on the `flaky (demo)` line with the real count
  staying 0; one fail-then-pass case runs under `-n 2` to prove the
  rerun-report forwarding works under xdist (the suite's default mode).
- Demo test itself is the e2e proof: every CI run on main publishes an
  Allure report containing one flaky-marked test with a visible retry.

## Out of scope

- Quarantine mechanism, flake-history storage, auto-detection thresholds.
- Any change to unit-test or local retry behavior.
- Failure Triage Agent integration (separate roadmap phase).
- The `tests/api/` opt-out hook itself — specified above, implemented with
  the API suite. (The `tests/framework/` opt-out hook is **in** scope —
  that layer already exists and would otherwise inherit retries.)
- WebKit-specific network-error taxonomy beyond the "Could not connect"
  fragment — if a WebKit infra failure surfaces with a different message,
  extend the regex then, with evidence.
