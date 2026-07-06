# Flaky Reliability: Deterministic Retry Policy — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Spec:** `docs/superpowers/specs/2026-07-06-flaky-retry-policy-design.md`

**Goal:** CI-only, bounded (max 1), infra-only test retries whose pass-on-retry outcomes are counted separately from clean passes, proven end-to-end by one deterministic demo test.

**Architecture:** A small pytest plugin (`utils/flaky_summary.py`, registered from root `conftest.py`) records `rerun` report outcomes and prints a distinct `flaky test summary` terminal section, mirrored to the GitHub Actions step summary. The framework test layer opts out of retries via a `pytest_collection_modifyitems` hook stamping `flaky(reruns=0)` (per-test markers beat the CLI `--reruns` flag). CI passes `--reruns=1 --only-rerun <infra regex>` through `docker compose run`; local runs keep `--reruns=0`.

**Tech Stack:** pytest 8, pytest-rerunfailures 15.0 (already pinned in `requirements.txt` — no dependency changes), pytest-xdist, `pytester` for plugin tests, GitHub Actions + Docker Compose.

**Two deliberate deviations from the spec's letter (same intent):**
1. Spec §2 says the hook lives in root `conftest.py`. It lives in `utils/flaky_summary.py` instead, registered via `pytest_plugins` in root `conftest.py`, because (a) root conftest already defines `pytest_runtest_logreport` at `conftest.py:148` and one module cannot hold two functions of the same name, and (b) the pytester tests load the exact production source into a sandbox — copying root-conftest source would execute its `pytest_configure`, which wipes the real `test-logs/` directory.
2. Spec §2 assumes `$GITHUB_STEP_SUMMARY` is visible to pytest. Pytest runs inside the compose container where that runner-side file is neither mounted nor in the environment. The workflow sets `GITHUB_STEP_SUMMARY` to a file under the already-mounted `test-logs/` volume and a follow-up step appends it to the real step summary.

## Global Constraints

- Python 3.12; ruff line length 88; ruff rules include `PTH` (use pathlib), `ARG` (no unused args — avoid by declaring only the hook parameters you use; pytest permits subset signatures), `I` (isort, first-party = `pages, tests, utils, config`).
- mypy `strict = true` with `disallow_untyped_defs` — every function including tests needs full annotations and `-> None` returns. Docstrings on modules, classes, and public functions.
- `--strict-markers` is on: any marker used with `@pytest.mark.<name>` must be registered in `pyproject.toml` `markers`.
- `addopts` must keep `--reruns=0` (`pyproject.toml:145`). CI overrides on the CLI; never change the default.
- Project rule: no Python logic (loops/conditionals/try-except/inline calculations) in test bodies — conditionals live in fixtures, hooks, or the plugin. Test bodies are flat call/assert sequences. (Inline test *sources fed to pytester* are string data, not project test bodies — conditionals inside them are fine but keep them minimal.)
- Local full-suite runs use `-n=auto` (xdist) — the plugin must work when reports are forwarded from workers to the controller.
- Verification commands per task: `ruff check <changed files>` and `mypy <changed files>` must both be clean before commit.
- pytester subprocess runs auto-load all installed plugins (playwright, allure, html) — they are inert without their CLI flags; expect each subprocess run to take ~1–2 s.

---

### Task 1: Flaky-summary plugin core (record reruns, print summary section)

**Files:**
- Create: `utils/flaky_summary.py`
- Create: `tests/framework/test_flaky_summary.py`
- Modify: `conftest.py` (root — add `pytest_plugins` registration near the top, after the imports at `conftest.py:26`)

**Interfaces:**
- Consumes: `rerun` outcome reports emitted by pytest-rerunfailures (`report.outcome == "rerun"`).
- Produces: pytest plugin module `utils.flaky_summary` with hook impls `pytest_configure() -> None`, `pytest_runtest_logreport(report: pytest.TestReport) -> None`, `pytest_terminal_summary(terminalreporter: TerminalReporter) -> None`, and helper `_summary_lines(flaky: list[str], failed: list[str]) -> list[str]`. Terminal section title is exactly `flaky test summary`; count lines are exactly `flaky (passed on retry): N` and `failed after retry: N`, each followed by two-space-indented nodeids. Task 2 extends this module; Tasks 4–6 rely on the line wording.

- [ ] **Step 1: Write the failing tests**

Create `tests/framework/test_flaky_summary.py`:

```python
"""Pytester tests for the flaky-summary plugin (``utils/flaky_summary.py``).

Each test copies the production plugin source into an isolated pytester
directory as that directory's ``conftest.py`` — the subprocess pytest run
then loads the exact code under test without sys.path manipulation — and
runs with retries enabled (``--reruns=1``) to simulate CI. No browser is
involved.
"""

from pathlib import Path

import pytest

from utils import flaky_summary

_PLUGIN_SOURCE = Path(flaky_summary.__file__).read_text()

_CLEAN_PASS = """
def test_passes() -> None:
    assert True
"""

# Fails attempt 1 (execution_count == 1), passes attempt 2 — deterministic.
_FAIL_THEN_PASS = """
import pytest


def test_recovers(request: pytest.FixtureRequest) -> None:
    assert getattr(request.node, "execution_count", 1) > 1
"""

_ALWAYS_FAILS = """
def test_always_fails() -> None:
    raise AssertionError("always fails")
"""


@pytest.fixture
def flaky_pytester(pytester: pytest.Pytester) -> pytest.Pytester:
    """A pytester sandbox whose conftest is the production plugin source."""
    pytester.makeconftest(_PLUGIN_SOURCE)
    return pytester


def test_clean_pass_prints_no_flaky_section(
    flaky_pytester: pytest.Pytester,
) -> None:
    flaky_pytester.makepyfile(_CLEAN_PASS)
    result = flaky_pytester.runpytest_subprocess("--reruns=1")
    result.assert_outcomes(passed=1)
    result.stdout.no_fnmatch_line("*flaky test summary*")


def test_fail_then_pass_is_counted_flaky(
    flaky_pytester: pytest.Pytester,
) -> None:
    flaky_pytester.makepyfile(_FAIL_THEN_PASS)
    result = flaky_pytester.runpytest_subprocess("--reruns=1")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(
        [
            "*flaky test summary*",
            "flaky (passed on retry): 1",
            "*test_recovers*",
        ]
    )


def test_fail_then_fail_lands_in_failed_after_retry(
    flaky_pytester: pytest.Pytester,
) -> None:
    flaky_pytester.makepyfile(_ALWAYS_FAILS)
    result = flaky_pytester.runpytest_subprocess("--reruns=1")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        [
            "failed after retry: 1",
            "*test_always_fails*",
        ]
    )
    result.stdout.no_fnmatch_line("*flaky (passed on retry)*")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/framework/test_flaky_summary.py -v`
Expected: collection ERROR with `ModuleNotFoundError: No module named 'utils.flaky_summary'` — the plugin does not exist yet. (The `pytester` fixture also does not exist yet; both are fixed in Step 3.)

- [ ] **Step 3: Write the plugin and register it**

Create `utils/flaky_summary.py`:

```python
"""Pytest plugin that makes retries loud: pass-on-retry counted separately.

Registered from the root ``conftest.py`` via ``pytest_plugins``. Records the
``rerun`` outcome reports emitted by pytest-rerunfailures and prints a
distinct ``flaky test summary`` terminal section. Inert when retries are
disabled (no rerun reports, no section) — i.e. every local run, and any
profile that disables the plugin outright (``-p no:rerunfailures``).

Works under xdist: workers forward reports to the controller, where
``pytest_terminal_summary`` runs.
"""

import pytest
from _pytest.terminal import TerminalReporter

_rerun_nodeids: set[str] = set()
_passed_nodeids: set[str] = set()


def pytest_configure() -> None:
    """Reset module state so repeated in-process runs start clean."""
    _rerun_nodeids.clear()
    _passed_nodeids.clear()


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Record rerun outcomes and final call-phase passes."""
    if report.outcome == "rerun":
        _rerun_nodeids.add(report.nodeid)
    elif report.when == "call" and report.passed:
        _passed_nodeids.add(report.nodeid)


def pytest_terminal_summary(terminalreporter: TerminalReporter) -> None:
    """Print flaky counts as their own terminal section."""
    flaky = sorted(_rerun_nodeids & _passed_nodeids)
    failed = sorted(_rerun_nodeids - _passed_nodeids)
    if not (flaky or failed):
        return
    terminalreporter.section("flaky test summary")
    for line in _summary_lines(flaky, failed):
        terminalreporter.line(line)


def _summary_lines(flaky: list[str], failed: list[str]) -> list[str]:
    """Build the summary lines: a count line per bucket, then its nodeids."""
    lines: list[str] = []
    if flaky:
        lines.append(f"flaky (passed on retry): {len(flaky)}")
        lines.extend(f"  {nodeid}" for nodeid in flaky)
    if failed:
        lines.append(f"failed after retry: {len(failed)}")
        lines.extend(f"  {nodeid}" for nodeid in failed)
    return lines
```

Modify root `conftest.py` — insert after the `logger = logging.getLogger(__name__)` line (`conftest.py:28`):

```python
# pytest_plugins may only be declared in the rootdir conftest.
# - utils.flaky_summary: retry observability (pass-on-retry counting);
#   lives in its own module so pytester tests can load the exact source.
# - pytester: enables the pytester fixture for framework plugin tests.
pytest_plugins = ["utils.flaky_summary", "pytester"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/framework/test_flaky_summary.py -v`
Expected: 3 passed.

- [ ] **Step 5: Static analysis**

Run: `ruff check utils/flaky_summary.py tests/framework/test_flaky_summary.py conftest.py && mypy utils/flaky_summary.py tests/framework/test_flaky_summary.py`
Expected: no findings.

- [ ] **Step 6: Guard against regressions in the existing suite**

Run: `pytest tests/framework/ -v`
Expected: all framework tests pass (the new `pytest_plugins` line must not disturb the existing suite).

- [ ] **Step 7: Commit**

```bash
git add utils/flaky_summary.py tests/framework/test_flaky_summary.py conftest.py
git commit -m "feat: flaky-summary pytest plugin counting pass-on-retry separately"
```

---

### Task 2: Demo bucket, GitHub step-summary mirror, xdist proof

**Files:**
- Modify: `utils/flaky_summary.py` (from Task 1)
- Modify: `tests/framework/test_flaky_summary.py` (from Task 1)

**Interfaces:**
- Consumes: Task 1's module and test fixtures (`flaky_pytester`, `_FAIL_THEN_PASS`).
- Produces: `flaky (demo): N` bucket keyed on the `flaky_demo` marker name appearing in `report.keywords`; step-summary mirror appending to the file named by `$GITHUB_STEP_SUMMARY`. Task 4's demo test and Task 5's workflow rely on both.

- [ ] **Step 1: Write the failing tests**

Append to `tests/framework/test_flaky_summary.py` — new inline source after `_ALWAYS_FAILS`:

```python
_DEMO_FAIL_THEN_PASS = """
import pytest


@pytest.mark.flaky_demo
def test_demo_recovers(request: pytest.FixtureRequest) -> None:
    assert getattr(request.node, "execution_count", 1) > 1
"""
```

and three new tests at the end of the file:

```python
def test_demo_marker_bucketed_separately(
    flaky_pytester: pytest.Pytester,
) -> None:
    flaky_pytester.makepyfile(_DEMO_FAIL_THEN_PASS)
    result = flaky_pytester.runpytest_subprocess("--reruns=1")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(
        [
            "flaky (demo): 1",
            "*test_demo_recovers*",
        ]
    )
    result.stdout.no_fnmatch_line("*flaky (passed on retry)*")


def test_xdist_forwards_rerun_reports(
    flaky_pytester: pytest.Pytester,
) -> None:
    flaky_pytester.makepyfile(_FAIL_THEN_PASS)
    result = flaky_pytester.runpytest_subprocess("--reruns=1", "-n", "2")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["flaky (passed on retry): 1"])


def test_summary_mirrored_to_github_step_summary(
    flaky_pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    summary_file = tmp_path / "step_summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
    flaky_pytester.makepyfile(_FAIL_THEN_PASS)
    result = flaky_pytester.runpytest_subprocess("--reruns=1")
    result.assert_outcomes(passed=1)
    assert "flaky (passed on retry): 1" in summary_file.read_text()
```

- [ ] **Step 2: Run tests to verify the new ones fail**

Run: `pytest tests/framework/test_flaky_summary.py -v`
Expected: `test_demo_marker_bucketed_separately` FAILS (no `flaky (demo)` line yet — the fail-then-pass lands in the real bucket) and `test_summary_mirrored_to_github_step_summary` FAILS (`FileNotFoundError` or assertion — nothing writes the file yet). `test_xdist_forwards_rerun_reports` already PASSES — it is a regression guard proving report forwarding, not new behavior. Task 1's 3 tests still pass.

- [ ] **Step 3: Extend the plugin**

Replace the full contents of `utils/flaky_summary.py` with:

```python
"""Pytest plugin that makes retries loud: pass-on-retry counted separately.

Registered from the root ``conftest.py`` via ``pytest_plugins``. Records the
``rerun`` outcome reports emitted by pytest-rerunfailures and prints a
distinct ``flaky test summary`` terminal section, mirrored to
``$GITHUB_STEP_SUMMARY`` when that variable is set (CI). Tests carrying the
``flaky_demo`` marker are bucketed on their own line so the real flaky count
starts at zero. Inert when retries are disabled (no rerun reports, no
section) — i.e. every local run, and any profile that disables the plugin
outright (``-p no:rerunfailures``).

Works under xdist: workers forward reports to the controller, where
``pytest_terminal_summary`` runs.
"""

import os
from pathlib import Path

import pytest
from _pytest.terminal import TerminalReporter

_rerun_nodeids: set[str] = set()
_demo_rerun_nodeids: set[str] = set()
_passed_nodeids: set[str] = set()


def pytest_configure() -> None:
    """Reset module state so repeated in-process runs start clean."""
    _rerun_nodeids.clear()
    _demo_rerun_nodeids.clear()
    _passed_nodeids.clear()


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Record rerun outcomes and final call-phase passes."""
    if report.outcome == "rerun":
        bucket = (
            _demo_rerun_nodeids
            if "flaky_demo" in report.keywords
            else _rerun_nodeids
        )
        bucket.add(report.nodeid)
    elif report.when == "call" and report.passed:
        _passed_nodeids.add(report.nodeid)


def pytest_terminal_summary(terminalreporter: TerminalReporter) -> None:
    """Print flaky counts as their own section; mirror to the CI step summary."""
    flaky = sorted(_rerun_nodeids & _passed_nodeids)
    demo = sorted(_demo_rerun_nodeids & _passed_nodeids)
    failed = sorted((_rerun_nodeids | _demo_rerun_nodeids) - _passed_nodeids)
    if not (flaky or demo or failed):
        return

    lines = _summary_lines(flaky, demo, failed)
    terminalreporter.section("flaky test summary")
    for line in lines:
        terminalreporter.line(line)

    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        content = "\n".join(["## Flaky test summary", "```", *lines, "```", ""])
        with Path(step_summary).open("a", encoding="utf-8") as fh:
            fh.write(content)


def _summary_lines(
    flaky: list[str], demo: list[str], failed: list[str]
) -> list[str]:
    """Build the summary lines: a count line per bucket, then its nodeids."""
    lines: list[str] = []
    if flaky:
        lines.append(f"flaky (passed on retry): {len(flaky)}")
        lines.extend(f"  {nodeid}" for nodeid in flaky)
    if demo:
        lines.append(f"flaky (demo): {len(demo)}")
        lines.extend(f"  {nodeid}" for nodeid in demo)
    if failed:
        lines.append(f"failed after retry: {len(failed)}")
        lines.extend(f"  {nodeid}" for nodeid in failed)
    return lines
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/framework/test_flaky_summary.py -v`
Expected: 6 passed.

- [ ] **Step 5: Static analysis**

Run: `ruff check utils/flaky_summary.py tests/framework/test_flaky_summary.py && mypy utils/flaky_summary.py tests/framework/test_flaky_summary.py`
Expected: no findings.

- [ ] **Step 6: Commit**

```bash
git add utils/flaky_summary.py tests/framework/test_flaky_summary.py
git commit -m "feat: demo bucket and CI step-summary mirror in flaky summary"
```

---

### Task 3: Framework layer opts out of retries

**Files:**
- Create: `tests/framework/conftest.py`
- Create: `tests/framework/test_retry_optout.py`

**Interfaces:**
- Consumes: pytest-rerunfailures rule that a per-test `flaky(reruns=0)` marker takes precedence over the CLI `--reruns` flag (verified in the installed 15.0 source, `get_reruns_count`).
- Produces: `tests/framework/conftest.py` with `pytest_collection_modifyitems(items: list[pytest.Item]) -> None` stamping `pytest.mark.flaky(reruns=0)` on every item under `tests/framework/` that does not carry the `flaky_demo` marker. Task 4 adds the `flaky_simulation` fixture to this same file and relies on the `flaky_demo` exemption.

- [ ] **Step 1: Write the failing tests**

Create `tests/framework/test_retry_optout.py`:

```python
"""Pytester tests for the framework layer's retry opt-out hook.

The framework layer stamps ``flaky(reruns=0)`` on its own items so it never
inherits CI's ``--reruns=1`` — except items marked ``flaky_demo``, which
exist to prove the retry pipeline. Tests copy the real
``tests/framework/conftest.py`` source into a pytester sandbox.
"""

from pathlib import Path

import pytest

_CONFTEST_SOURCE = (Path(__file__).parent / "conftest.py").read_text()

_ALWAYS_FAILS = """
def test_always_fails() -> None:
    raise AssertionError("always fails")
"""

_DEMO_FAIL_THEN_PASS = """
import pytest


@pytest.mark.flaky_demo
def test_demo_recovers(request: pytest.FixtureRequest) -> None:
    assert getattr(request.node, "execution_count", 1) > 1
"""

# Both fail attempt 1 and pass attempt 2 — but only the one OUTSIDE the
# conftest's directory may retry, so the inside one must simply fail.
_RECOVERS_INSIDE = """
import pytest


def test_recovers_inside(request: pytest.FixtureRequest) -> None:
    assert getattr(request.node, "execution_count", 1) > 1
"""

_RECOVERS_OUTSIDE = """
import pytest


def test_recovers_outside(request: pytest.FixtureRequest) -> None:
    assert getattr(request.node, "execution_count", 1) > 1
"""


def test_framework_items_never_rerun(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(_CONFTEST_SOURCE)
    pytester.makepyfile(_ALWAYS_FAILS)
    result = pytester.runpytest_subprocess("--reruns=1")
    result.assert_outcomes(failed=1)
    result.stdout.no_fnmatch_line("*1 rerun*")


def test_flaky_demo_marker_stays_retry_eligible(
    pytester: pytest.Pytester,
) -> None:
    pytester.makeconftest(_CONFTEST_SOURCE)
    pytester.makepyfile(_DEMO_FAIL_THEN_PASS)
    result = pytester.runpytest_subprocess("--reruns=1")
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines(["*1 rerun*"])


def test_optout_scoped_to_conftest_directory(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(
        **{
            "framework/conftest": _CONFTEST_SOURCE,
            "framework/test_inside": _RECOVERS_INSIDE,
            "test_outside": _RECOVERS_OUTSIDE,
        }
    )
    result = pytester.runpytest_subprocess("--reruns=1")
    result.assert_outcomes(passed=1, failed=1)
```

(The third test is the load-bearing one: `pytest_collection_modifyitems` in a subdirectory conftest receives ALL collected items, so without the path filter the framework conftest would silently strip retries from the e2e suites too. Inside item: stamped, no retry, fails. Outside item: retries, passes.)

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/framework/test_retry_optout.py -v`
Expected: collection ERROR with `FileNotFoundError` — `tests/framework/conftest.py` does not exist yet.

- [ ] **Step 3: Write the conftest hook**

Create `tests/framework/conftest.py`:

```python
"""Framework-layer pytest configuration.

Retry eligibility is a property of the test layer: only browser-driven e2e
tests fail on infra noise, so only they may retry. This layer's unit tests
fail on logic — a retry could only mask a bug — so every item is stamped
``flaky(reruns=0)``, which takes precedence over any CLI ``--reruns`` flag.
The ``flaky_demo``-marked test is exempt: it exists to prove the retry
pipeline and must stay retry-eligible.
"""

from pathlib import Path

import pytest

_FRAMEWORK_DIR = Path(__file__).parent


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Opt this layer out of retries, except the ``flaky_demo`` test.

    Collection hooks receive ALL collected items, not just this directory's
    — the path filter keeps the stamp from leaking onto the e2e suites.
    """
    for item in items:
        outside_layer = not item.path.is_relative_to(_FRAMEWORK_DIR)
        if outside_layer or item.get_closest_marker("flaky_demo"):
            continue
        item.add_marker(pytest.mark.flaky(reruns=0))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/framework/test_retry_optout.py -v`
Expected: 3 passed.

- [ ] **Step 5: Static analysis and full framework suite**

Run: `ruff check tests/framework/ && mypy tests/framework/conftest.py tests/framework/test_retry_optout.py && pytest tests/framework/ -v`
Expected: no findings; all framework tests pass (the stamp is inert at `--reruns=0`).

- [ ] **Step 6: Commit**

```bash
git add tests/framework/conftest.py tests/framework/test_retry_optout.py
git commit -m "test: opt framework layer out of the CI retry policy"
```

---

### Task 4: Deterministic flaky demo test

**Files:**
- Create: `tests/framework/test_flaky_demo.py`
- Modify: `tests/framework/conftest.py` (add the `flaky_simulation` fixture)
- Modify: `pyproject.toml` (register `flaky_demo` marker in `markers` at `pyproject.toml:147-163`; add policy comment above `--reruns=0` in `addopts` at `pyproject.toml:145`)

**Interfaces:**
- Consumes: Task 3's `flaky_demo` exemption; Task 2's `flaky (demo)` bucket; `request.node.execution_count` set by pytest-rerunfailures (starts at 1; absent when the plugin is disabled — hence the `getattr` default).
- Produces: fixture `flaky_simulation(request: pytest.FixtureRequest) -> None` in `tests/framework/conftest.py`; test `test_deterministic_flaky_demo` marked `@pytest.mark.flaky_demo`; registered marker `flaky_demo`. Task 5's CI run and Task 6's README reference this test.

- [ ] **Step 1: Register the marker and document the retry default**

In `pyproject.toml`, replace the line `    "--reruns=0",` (inside `addopts`) with:

```toml
    # Retries default OFF everywhere. CI (and only CI) overrides on the
    # pytest CLI with `--reruns=1 --only-rerun <infra regex>` — see
    # .github/workflows/tests.yml. Retries are an observability mechanism,
    # not a fix: assertion failures never retry, and pass-on-retry is
    # counted separately (utils/flaky_summary.py).
    "--reruns=0",
```

In the `markers` list, add after the `"acceptapayment: ..."` entry:

```toml
    "flaky_demo: Deterministic retry-pipeline demo; exempt from the framework layer's retry opt-out",
```

- [ ] **Step 2: Write the demo test (this is the failing test for this task)**

Create `tests/framework/test_flaky_demo.py`:

```python
"""Deterministic flaky demo: proves the retry pipeline end to end.

Runs in every CI run so the published Allure report always contains one
retried, flaky-marked test. The flaky-summary plugin counts it on its own
``flaky (demo)`` line, never in the real flaky total. Deterministic — the
flake reproduces 100% of the time; no randomness.
"""

import allure
import pytest


@pytest.mark.flaky_demo
@allure.title("Flaky retry demo — deterministic fail-then-pass")
@allure.description(
    "Intentionally fails its first attempt with a Playwright TimeoutError "
    "and passes on the retry. Demonstrates the CI retry policy and "
    "pass-on-retry reporting; it is not a test of the application. "
    "Skips locally, where retries are disabled (--reruns=0)."
)
def test_deterministic_flaky_demo(flaky_simulation: None) -> None:
    """Passes only on attempt 2; the fixture raises on attempt 1."""
```

- [ ] **Step 3: Run to verify it fails for the right reason**

Run: `pytest tests/framework/test_flaky_demo.py -v`
Expected: ERROR with `fixture 'flaky_simulation' not found` — the fixture does not exist yet.

- [ ] **Step 4: Write the fixture**

Append to `tests/framework/conftest.py` (after the `pytest_collection_modifyitems` hook), and add the playwright import to the import block at the top:

```python
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
```

```python
@pytest.fixture
def flaky_simulation(request: pytest.FixtureRequest) -> None:
    """Deterministically fail attempt 1 with an infra-shaped error.

    Keyed on ``request.node.execution_count`` (set by pytest-rerunfailures,
    starts at 1); the ``getattr`` default covers profiles that disable the
    plugin outright (mutmut runs ``-p no:rerunfailures``), where the option
    lookup below also falls back to 0 and the test skips. Raises Playwright
    ``TimeoutError`` so the failure matches the CI ``--only-rerun`` regex.
    """
    reruns: int = request.config.getoption("--reruns", default=0) or 0
    if reruns == 0:
        pytest.skip(
            "flaky demo is meaningful only with retries enabled "
            "(CI passes --reruns=1); skipping on retry-less runs"
        )
    if getattr(request.node, "execution_count", 1) == 1:
        raise PlaywrightTimeoutError(
            "simulated infrastructure flake: attempt 1 always times out"
        )
```

- [ ] **Step 5: Verify both behaviors**

Run: `pytest tests/framework/test_flaky_demo.py -v`
Expected: 1 skipped (local runs keep `--reruns=0` from addopts).

Run: `pytest tests/framework/test_flaky_demo.py --reruns=1 -v`
Expected: 1 passed, 1 rerun; terminal output contains the `flaky test summary` section with `flaky (demo): 1` and NO `flaky (passed on retry)` line.

- [ ] **Step 6: Static analysis and full framework suite**

Run: `ruff check tests/framework/ && mypy tests/framework/ && pytest tests/framework/ -v`
Expected: no findings; all framework tests pass, demo shows as skipped.

- [ ] **Step 7: Commit**

```bash
git add tests/framework/test_flaky_demo.py tests/framework/conftest.py pyproject.toml
git commit -m "feat: deterministic flaky demo test proving the retry pipeline"
```

---

### Task 5: CI workflow — bounded infra-only retries

**Files:**
- Modify: `.github/workflows/tests.yml` (the "Run tests" step at `.github/workflows/tests.yml:62-63`, plus one new step after it)

**Interfaces:**
- Consumes: compose arg pass-through (args after the service name go straight to pytest — same mechanism as `--browser`); the `./test-logs:/work/test-logs` volume mount (`docker-compose.yml:27`); Task 2's step-summary mirror keyed on `$GITHUB_STEP_SUMMARY`.
- Produces: CI runs with `--reruns=1 --only-rerun "TimeoutError|net::ERR|NS_ERROR_|Could not connect"`; flaky summary visible on the Actions run page.

- [ ] **Step 1: Replace the "Run tests" step and add the bridge step**

Replace lines 62–63 of `.github/workflows/tests.yml`:

```yaml
      - name: Run tests (${{ matrix.browser }})
        run: docker compose run --rm tests --browser=${{ matrix.browser }}
```

with:

```yaml
      # Retry policy: CI-only, browser-e2e-only, max 1 retry, and only for
      # infra-shaped failures — assertion failures never retry. The regex
      # covers Playwright TimeoutError (all browsers), Chromium net::ERR_*,
      # Firefox NS_ERROR_*, and WebKit's freeform "Could not connect".
      # GITHUB_STEP_SUMMARY inside the container points at a file under the
      # mounted test-logs/ volume; the step below bridges it to the runner's
      # real step summary (the runner-side file is not visible in-container).
      - name: Run tests (${{ matrix.browser }})
        run: >-
          docker compose run --rm
          -e GITHUB_STEP_SUMMARY=/work/test-logs/flaky-summary.md
          tests --browser=${{ matrix.browser }}
          --reruns=1 --only-rerun "TimeoutError|net::ERR|NS_ERROR_|Could not connect"

      - name: Publish flaky summary to run page
        if: always()
        run: |
          if [ -s test-logs/flaky-summary.md ]; then
            cat test-logs/flaky-summary.md >> "$GITHUB_STEP_SUMMARY"
          fi
```

- [ ] **Step 2: Validate the workflow file**

Run: `python3 -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('.github/workflows/tests.yml').read_text()); print('workflow yaml ok')"`
Expected: `workflow yaml ok`. If `actionlint` is installed, also run `actionlint .github/workflows/tests.yml` — expected: no findings.

- [ ] **Step 3: Prove CLI pass-through locally (no live run needed)**

Run: `docker compose run --rm tests --collect-only -q --reruns=1 --only-rerun "TimeoutError|net::ERR" 2>&1 | tail -5` — only if the Docker stack is available locally; otherwise skip with a note in the task report (the pytester suite plus CI itself cover the behavior).
Expected: pytest collects without "unrecognized arguments" errors.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/tests.yml
git commit -m "ci: bounded infra-only retry policy with flaky step summary"
```

---

### Task 6: README — policy subsection and roadmap entry

**Files:**
- Modify: `README.md` (roadmap table at `README.md:44-53`; new section after the Roadmap section's closing `---` at `README.md:55`)

**Interfaces:**
- Consumes: Task 4's demo test path; Task 2's summary line wording; the live Allure report URL already in the README.
- Produces: documentation only.

- [ ] **Step 1: Add the roadmap row**

In the Roadmap table, insert after the `| Performance Testing | Planned | ... |` row:

```markdown
| Flaky Quarantine & Auto-Detection | Planned | History-based flake detection, auto-quarantine marker; feeds the Failure Triage Agent |
```

- [ ] **Step 2: Add the policy subsection**

Insert after the Roadmap section's closing `---` (before `## AI Components (Planned)`):

```markdown
## Flaky Reliability

Retries are an observability mechanism, not a fix. CI — and only CI — runs
e2e tests with `--reruns=1`, restricted via `--only-rerun` to
infrastructure-shaped failures (Playwright timeouts, browser network
errors); an assertion failure never retries, and non-browser test layers
opt out entirely. Tests that pass only on retry are counted separately from
clean passes: a `flaky (passed on retry)` section in the pytest output and
on the Actions run page, plus the Retries view in the
[live Allure report](https://summerduck.github.io/fintech-playwright-quality/).
One deterministic demo test (`tests/framework/test_flaky_demo.py`) fails its
first attempt in every CI run to prove the pipeline end to end; it is
counted on its own `flaky (demo)` line so any nonzero real flake count is
unambiguous signal.

---
```

- [ ] **Step 3: Verify rendering**

Run: `grep -n "Flaky" README.md`
Expected: hits in the roadmap table and the new section; visually confirm the table still renders (pipe count matches other rows).

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: flaky reliability policy and quarantine roadmap entry"
```

---

## Final verification (after all tasks)

- [ ] Run: `pytest tests/framework/ -v` — expected: all pass, demo skipped, no flaky section (retries off locally).
- [ ] Run: `pytest tests/framework/ --reruns=1 -v` — expected: all pass, demo shows `1 rerun`, summary shows `flaky (demo): 1` and no real-flake line (the opt-out stamp keeps every other framework test at 0 reruns).
- [ ] Run: `ruff check . && mypy utils/ tests/framework/` — expected: clean.
- [ ] Push and confirm on the Actions run page: step summary shows the `Flaky test summary` block with `flaky (demo): 1` per matrix leg; the published Allure report shows the demo test with a retry.
