# JUnit Gate for the Project Test Suite — Design

**Date:** 2026-07-17
**Status:** Approved (brainstorm), pending implementation plan

## Problem

CI judges the test run by the pytest step's process exit code. That code has
two blind spots the exit code cannot express:

- **All tests skipped** — a broad skip (wrong env, missing key, a module-level
  `pytestmark = skip`) makes pytest exit `0` while verifying nothing. The
  `env` fixture is single-valued (`prod|local|docker`), so a misconfigured run
  can silently disable a whole file.
- **A swallowed non-zero code** — `|| true`, a trailing shell command, or a
  container layer can eat pytest's honest non-zero exit (e.g. `5` = no tests
  collected), turning it into a false green.

`demos/false_green/` demonstrates these shapes. This spec promotes that demo's
idea into a real gate for the production suite.

Note: `0 tests collected` alone already exits `5` and fails the step today; the
gate's unique value is catching the shapes the exit code hides or that get
swallowed — and doing so from an independent source of truth (the report).

## Chosen Approach — A: separate CI gate step

Three units, each with one responsibility:

```
pytest run ──writes──> test-results/junit.xml ──read by──> utils/junit_gate.py ──> exit 0/1
  (honest red via $?)      (structured truth)              (catches $? blind spots)
```

**Why A over the alternatives:**

- **vs. pytest plugin / `pytest_sessionfinish` hook** — a hook re-couples the
  gate to the process exit code, the exact thing the demo argues against, and
  makes the judge nearly impossible to unit-test. A's gate is a plain module
  with its own exit code and its own tests.
- **vs. cross-matrix aggregator (C)** — C is the only shape that catches "one
  browser silently shrank," but it needs artifact upload/download and job
  dependencies. The matrix runs the *same* suite per browser, so cross-browser
  count divergence would be a collection bug, not normal — YAGNI for v1. A
  per-job gate still fails the specific browser's job if that browser collects
  zero. C can be added later only if real divergence appears.

## Components

`utils/junit_gate.py` — pure judge module, stdlib only (`xml.etree`), living
alongside `flaky_summary.py` / `run_record.py` as a framework utility.

```python
def parse_junit(path: str) -> Dict[str, int]
    # Sum tests/failures/errors/skipped across every <testsuite>.
    # passed = tests - failures - errors - skipped.

def evaluate_gate(counts: Dict[str, int]) -> tuple[bool, str]
    # (ok, reason). ok=True -> CI green; ok=False -> fail the step.

def main() -> int
    # print the report line, run the gate, return 0 | 1 | 2 (usage).
```

`counts` keys: `tests, passed, failures, errors, skipped` — 1:1 with the demo's
`parse_junit`, reusing that proven structure.

## pytest wiring

Add `--junitxml=test-results/junit.xml` to `addopts` in `pyproject.toml`,
next to the existing `--alluredir` / `--html` (report artifacts are universal,
unlike the CI-only `--reruns` override). Inside the container this resolves to
`/work/test-results/junit.xml`, which is mounted to `./test-results/` on the
runner (mount already exists in `docker-compose.yml`).

## CI wiring (`.github/workflows/tests.yml`)

After the "Run tests (${{ matrix.browser }})" step, add a step:

```yaml
- name: JUnit gate (${{ matrix.browser }})
  if: always()
  run: python3 utils/junit_gate.py test-results/junit.xml
```

- `if: always()` so the gate still runs when the test step failed — otherwise
  the gate would go quiet exactly when the suite is red.
- Runs on the runner (GitHub `ubuntu` images ship `python3`; the module is
  stdlib-only, so no container needed).
- Runs per browser job. No cross-job coordination.

## Gate policy

Checks ordered specific → general (so the most specific cause wins the reason
label — the guard-ordering lesson debugged in the demo):

| Condition | Result | Reason |
|---|---|---|
| file missing / unparseable XML | FAIL (exit 1) | `no junit report — run produced no result` |
| `tests == 0` | FAIL | `no tests collected` |
| `failures + errors > 0` | FAIL | `test failures/errors` |
| `passed == 0` | FAIL | `all tests skipped` |
| otherwise | PASS (exit 0) | `N passed` |

**Deviations from the demo policy (both deliberate):**

- **Missing/unparseable report → FAIL, not a crash.** The demo reads a trusted
  local file; in CI a run that crashed before writing the report is itself a
  false-green signal. The gate must treat an absent report as failure.
- **`errors > 0` flagged alongside `failures > 0`** (defense-in-depth). Since
  the gate insures the swallow-able exit code, collection/fixture errors are
  the same honest-red class and are covered too.

**Explicitly out of scope:**

- **No min-tests floor / shrinkage protection.** A silently *shrunk* suite
  (e.g. 200 → 40 tests, all green) will NOT trip this gate. Decided against a
  threshold to keep v1 minimal. This is a known, accepted boundary of the tool,
  not an oversight — documented so it is a conscious limit.

## Testing

`tests/framework/test_junit_gate.py`, `@pytest.mark.unit`, AAA pattern:

- `evaluate_gate` — one case per policy row: empty, all-skipped, failures,
  errors, healthy.
- `parse_junit` — a temp XML file (healthy + multi-`<testsuite>`), plus a
  missing path and a malformed file to prove they degrade to a FAIL reason
  rather than raising.

The point of approach A is a judge that is itself testable; these tests are
what make the gate trustworthy.

## Reference

- Google TAP model: results flow as typed records (PASSED/FAILED/SKIPPED),
  sidestepping the single-exit-code failure mode. This gate is a local
  reconstruction of that distinction over `junit.xml`.
  - <https://research.google.com/pubs/archive/45861.pdf>
  - <https://abseil.io/resources/swe-book/html/ch14.html>
- `demos/false_green/` — the walkthrough this gate productionizes.
