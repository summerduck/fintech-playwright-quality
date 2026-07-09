# Flaky Reliability v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the flaky-test lifecycle: quarantine marker (contain), durable per-test flake history (remember), threshold-based candidate detection (decide) — per the approved spec `docs/superpowers/specs/2026-07-09-flaky-reliability-v2-design.md`.

**Architecture:** Two small pytest plugins (`utils/quarantine.py`, `utils/run_record.py`) registered from the root `conftest.py` via `pytest_plugins`, mirroring v1's `utils/flaky_summary.py` pattern, plus one stdlib-only analysis script (`scripts/analyze_flake_history.py`) that runs in the existing `publish-report` CI job and writes `history.json` + `candidates.md` to gh-pages. The analyzer proposes; humans apply markers via reviewed PRs.

**Tech Stack:** Python 3.12, pytest + pytester, pytest-rerunfailures (existing), pytest-xdist (existing), GitHub Actions. The analyzer is stdlib-only (runs on the bare runner, no pip install).

## Global Constraints

- Python 3.12, line length 88, `snake_case`/`PascalCase`/`UPPER_CASE` per PEP 8.
- mypy `strict = true` applies to `utils/` and `scripts/` (pre-commit mypy excludes `^tests/`).
- Ruff rules from `pyproject.toml` (`E,F,I,N,UP,B,C4,SIM,RET,ARG,PTH,ERA,PL`); verify with `ruff check <files>` and `ruff format --check <files>`.
- Commit messages use conventional prefixes: `feat:`/`fix:`/`test:`/`ci:`/`docs:`.
- Do NOT type `.venv` (or any string containing `.env`) in Bash commands — a repo hook blocks them. Use plain `pytest` / `python -m pytest`.
- pytester tests copy production plugin source with `Path(module.__file__).read_text()` and `pytester.makeconftest(...)` — the exact pattern of `tests/framework/test_flaky_summary.py`.
- Detection constants (from spec): stored window 50, detect window 30, freshness window 10, fail-streak 3, fail rate ≥5% over ≥10 runs, release streak 10 XPASS, expiry warning 7 days, suggested quarantine TTL 30 days.

---

### Task 1: Quarantine marker plugin (`utils/quarantine.py`)

**Files:**
- Create: `utils/quarantine.py`
- Create: `tests/framework/test_quarantine.py`
- Modify: `conftest.py:34` (add `"utils.quarantine"` to `pytest_plugins`)

**Interfaces:**
- Consumes: nothing (self-contained pytest plugin).
- Produces: marker `@pytest.mark.quarantine(reason: str, expires: str)`; constant `QUARANTINE_EXPIRES_PROPERTY = "quarantine_expires"`; for each valid quarantined item, appends `("quarantine_expires", "<ISO date>")` to `item.user_properties` (Task 2 reads this from `TestReport.user_properties`).

- [ ] **Step 1: Write the failing tests**

Create `tests/framework/test_quarantine.py`:

```python
"""Pytester tests for the quarantine plugin (``utils/quarantine.py``).

Each test copies the production plugin source into an isolated pytester
directory as that directory's ``conftest.py`` — the pattern of
``test_flaky_summary.py`` — so the subprocess run loads the exact code under
test. No browser is involved.
"""

from pathlib import Path

import pytest

from utils import quarantine

_PLUGIN_SOURCE = Path(quarantine.__file__).read_text()

_QUARANTINED_FAILING = """
import pytest


@pytest.mark.quarantine(reason="JIRA-1: flaky dashboard", expires="2099-01-01")
def test_shielded_failure() -> None:
    raise AssertionError("flaky failure")
"""

_QUARANTINED_PASSING = """
import pytest


@pytest.mark.quarantine(reason="JIRA-1: flaky dashboard", expires="2099-01-01")
def test_shielded_pass() -> None:
    assert True
"""

_EXPIRED = """
import pytest


@pytest.mark.quarantine(reason="JIRA-1: flaky dashboard", expires="2020-01-01")
def test_expired() -> None:
    assert True
"""

_MISSING_EXPIRES = """
import pytest


@pytest.mark.quarantine(reason="JIRA-1: flaky dashboard")
def test_missing_expires() -> None:
    assert True
"""

_MISSING_REASON = """
import pytest


@pytest.mark.quarantine(expires="2099-01-01")
def test_missing_reason() -> None:
    assert True
"""

_BAD_DATE = """
import pytest


@pytest.mark.quarantine(reason="JIRA-1: flaky dashboard", expires="next month")
def test_bad_date() -> None:
    assert True
"""

_UNMARKED = """
def test_untouched() -> None:
    assert True
"""


@pytest.fixture
def quarantine_pytester(pytester: pytest.Pytester) -> pytest.Pytester:
    """A pytester sandbox whose conftest is the production plugin source."""
    pytester.makeconftest(_PLUGIN_SOURCE)
    return pytester


def test_quarantined_failure_becomes_xfail_and_run_stays_green(
    quarantine_pytester: pytest.Pytester,
) -> None:
    quarantine_pytester.makepyfile(_QUARANTINED_FAILING)
    result = quarantine_pytester.runpytest_subprocess()
    result.assert_outcomes(xfailed=1)
    assert result.ret == 0


def test_quarantined_pass_is_recorded_as_xpass(
    quarantine_pytester: pytest.Pytester,
) -> None:
    quarantine_pytester.makepyfile(_QUARANTINED_PASSING)
    result = quarantine_pytester.runpytest_subprocess()
    result.assert_outcomes(xpassed=1)
    assert result.ret == 0


def test_expired_marker_aborts_the_run_naming_the_test(
    quarantine_pytester: pytest.Pytester,
) -> None:
    quarantine_pytester.makepyfile(_EXPIRED)
    result = quarantine_pytester.runpytest_subprocess()
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*test_expired*expired on 2020-01-01*"])


def test_missing_expires_is_rejected(
    quarantine_pytester: pytest.Pytester,
) -> None:
    quarantine_pytester.makepyfile(_MISSING_EXPIRES)
    result = quarantine_pytester.runpytest_subprocess()
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*requires reason= and expires=*"])


def test_missing_reason_is_rejected(
    quarantine_pytester: pytest.Pytester,
) -> None:
    quarantine_pytester.makepyfile(_MISSING_REASON)
    result = quarantine_pytester.runpytest_subprocess()
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*requires reason= and expires=*"])


def test_non_iso_expires_is_rejected(
    quarantine_pytester: pytest.Pytester,
) -> None:
    quarantine_pytester.makepyfile(_BAD_DATE)
    result = quarantine_pytester.runpytest_subprocess()
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*must be an ISO date*"])


def test_unmarked_test_is_untouched(
    quarantine_pytester: pytest.Pytester,
) -> None:
    quarantine_pytester.makepyfile(_UNMARKED)
    result = quarantine_pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/framework/test_quarantine.py -v`
Expected: collection error — `ModuleNotFoundError: No module named 'utils.quarantine'` (or ImportError). That IS the failing state.

- [ ] **Step 3: Write the plugin**

Create `utils/quarantine.py`:

```python
"""Pytest plugin: quarantine marker — run flaky tests without blocking merges.

Registered from the root ``conftest.py`` via ``pytest_plugins``. A test marked
``@pytest.mark.quarantine(reason=..., expires=...)`` is converted at
collection time to ``xfail(strict=False)``: failures become XFAIL, passes
become XPASS, and neither blocks the run. The marker in the test file IS the
quarantine list — ``git grep quarantine`` enumerates it.

Hygiene is enforced at collection:
- ``reason`` and ``expires`` (ISO date) are both required;
- an ``expires`` date in the past aborts the run with ``UsageError`` naming
  every expired test — fix or extend, never silent decay.

Side effect worth knowing: pytest-rerunfailures does not rerun xfailed tests,
so quarantined tests stop consuming the CI retry budget. The expiry date is
stamped onto ``item.user_properties`` so the run-record plugin
(``utils/run_record.py``) can report quarantine state without re-reading
markers — user properties travel with reports across xdist workers.
"""

import datetime as dt

import pytest

QUARANTINE_EXPIRES_PROPERTY = "quarantine_expires"


def pytest_configure(config: pytest.Config) -> None:
    """Register the marker so ``--strict-markers`` accepts it."""
    config.addinivalue_line(
        "markers",
        "quarantine(reason, expires): run but never block — converted to "
        "xfail(strict=False); an expired ISO 'expires' date aborts collection",
    )


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Convert quarantine markers to non-strict xfail; abort on invalid ones."""
    errors: list[str] = []
    today = dt.date.today()
    for item in items:
        marker = item.get_closest_marker("quarantine")
        if marker is None:
            continue
        problem = _apply_quarantine(item, marker, today)
        if problem:
            errors.append(problem)
    if errors:
        raise pytest.UsageError("\n".join(errors))


def _apply_quarantine(
    item: pytest.Item, marker: pytest.Mark, today: dt.date
) -> str | None:
    """Validate marker kwargs and add the xfail shield; return the error text."""
    reason = marker.kwargs.get("reason")
    expires_raw = marker.kwargs.get("expires")
    if not reason or not expires_raw:
        return f"{item.nodeid}: quarantine marker requires reason= and expires="
    try:
        expires = dt.date.fromisoformat(expires_raw)
    except (TypeError, ValueError):
        return (
            f"{item.nodeid}: quarantine expires= must be an ISO date "
            f"(YYYY-MM-DD), got {expires_raw!r}"
        )
    if expires < today:
        return (
            f"{item.nodeid}: quarantine expired on {expires_raw} "
            f"(reason: {reason}) — fix the test or extend the date"
        )
    item.add_marker(pytest.mark.xfail(reason=f"quarantined: {reason}", strict=False))
    item.user_properties.append((QUARANTINE_EXPIRES_PROPERTY, expires_raw))
    return None
```

Then modify `conftest.py` — replace the `pytest_plugins` block:

```python
# pytest_plugins may only be declared in the rootdir conftest.
# - utils.flaky_summary: retry observability (pass-on-retry counting);
#   lives in its own module so pytester tests can load the exact source.
# - utils.quarantine: quarantine marker -> xfail(strict=False) conversion.
# - pytester: enables the pytester fixture for framework plugin tests.
pytest_plugins = ["utils.flaky_summary", "utils.quarantine", "pytester"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/framework/test_quarantine.py -v`
Expected: 7 passed.

- [ ] **Step 5: Static checks**

Run: `ruff check utils/quarantine.py tests/framework/test_quarantine.py conftest.py && ruff format --check utils/quarantine.py tests/framework/test_quarantine.py && mypy utils/quarantine.py`
Expected: no findings. Fix anything reported before committing.

- [ ] **Step 6: Commit**

```bash
git add utils/quarantine.py tests/framework/test_quarantine.py conftest.py
git commit -m "feat: quarantine marker plugin — run flaky tests without blocking (xfail shield, enforced expiry)"
```

---

### Task 2: Run-record plugin (`utils/run_record.py`)

**Files:**
- Create: `utils/run_record.py`
- Create: `tests/framework/test_run_record.py`
- Modify: `conftest.py` (`pytest_plugins` gains `"utils.run_record"`)

**Interfaces:**
- Consumes: `("quarantine_expires", "<ISO date>")` entries in `TestReport.user_properties` (produced by Task 1).
- Produces: `test-logs/run-records/run-record-<browser>.json` at session end, schema per spec: `{"schema": 1, "run_id", "sha", "branch", "browser", "timestamp", "tests": [{"nodeid", "outcome", "reruns", "quarantined", "expires"?}]}`. Outcome vocabulary: `passed | failed | xfailed | xpassed | skipped`. Task 3's analyzer consumes these files.

- [ ] **Step 1: Write the failing tests**

Create `tests/framework/test_run_record.py`:

```python
"""Pytester tests for the run-record plugin (``utils/run_record.py``).

The quarantined-entry test simulates Task 1's plugin output (an xfail marker
plus a ``quarantine_expires`` user property) instead of loading both plugins
into one sandbox conftest — two modules defining the same hooks cannot be
concatenated. The real two-plugin integration is exercised by the demo test
in the live suite (``test_quarantine_demo.py``).
"""

import json
from pathlib import Path
from typing import Any

import pytest

from utils import run_record

_PLUGIN_SOURCE = Path(run_record.__file__).read_text()

_MIXED_OUTCOMES = """
import pytest


def test_passes() -> None:
    assert True


def test_fails() -> None:
    raise AssertionError("boom")


@pytest.mark.skip(reason="not today")
def test_skipped() -> None:
    assert True
"""

_RETRY_RECOVERS = """
import pytest


def test_recovers(request: pytest.FixtureRequest) -> None:
    assert getattr(request.node, "execution_count", 1) > 1
"""

_SIMULATED_QUARANTINE = """
import pytest


@pytest.mark.xfail(reason="quarantined: demo", strict=False)
def test_shielded(request: pytest.FixtureRequest) -> None:
    request.node.user_properties.append(("quarantine_expires", "2099-01-01"))
    raise AssertionError("still flaky")
"""


@pytest.fixture
def record_pytester(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> pytest.Pytester:
    """Sandbox with CI env vars set so the recorder is active."""
    monkeypatch.setenv("GITHUB_RUN_ID", "424242")
    monkeypatch.setenv("GITHUB_SHA", "abc1234")
    monkeypatch.setenv("GITHUB_REF_NAME", "main")
    pytester.makeconftest(_PLUGIN_SOURCE)
    return pytester


def _record(pytester: pytest.Pytester) -> dict[str, Any]:
    path = pytester.path / "test-logs" / "run-records" / "run-record-default.json"
    data: dict[str, Any] = json.loads(path.read_text())
    return data


def _tests_by_name(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {t["nodeid"].rsplit("::", 1)[-1]: t for t in record["tests"]}


def test_outcomes_and_run_metadata_recorded(
    record_pytester: pytest.Pytester,
) -> None:
    record_pytester.makepyfile(_MIXED_OUTCOMES)
    record_pytester.runpytest_subprocess()
    record = _record(record_pytester)
    tests = _tests_by_name(record)
    assert record["schema"] == 1
    assert record["run_id"] == "424242"
    assert record["sha"] == "abc1234"
    assert record["branch"] == "main"
    assert tests["test_passes"]["outcome"] == "passed"
    assert tests["test_fails"]["outcome"] == "failed"
    assert tests["test_skipped"]["outcome"] == "skipped"


def test_reruns_counted_with_final_pass(
    record_pytester: pytest.Pytester,
) -> None:
    record_pytester.makepyfile(_RETRY_RECOVERS)
    result = record_pytester.runpytest_subprocess("--reruns=1")
    result.assert_outcomes(passed=1)
    tests = _tests_by_name(_record(record_pytester))
    assert tests["test_recovers"]["outcome"] == "passed"
    assert tests["test_recovers"]["reruns"] == 1


def test_quarantined_entry_carries_flag_and_expires(
    record_pytester: pytest.Pytester,
) -> None:
    record_pytester.makepyfile(_SIMULATED_QUARANTINE)
    result = record_pytester.runpytest_subprocess()
    result.assert_outcomes(xfailed=1)
    tests = _tests_by_name(_record(record_pytester))
    assert tests["test_shielded"]["outcome"] == "xfailed"
    assert tests["test_shielded"]["quarantined"] is True
    assert tests["test_shielded"]["expires"] == "2099-01-01"


def test_inert_without_github_run_id(
    record_pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GITHUB_RUN_ID")
    record_pytester.makepyfile(_MIXED_OUTCOMES)
    record_pytester.runpytest_subprocess()
    assert not (record_pytester.path / "test-logs" / "run-records").exists()


def test_xdist_controller_writes_exactly_one_complete_file(
    record_pytester: pytest.Pytester,
) -> None:
    record_pytester.makepyfile(_MIXED_OUTCOMES)
    record_pytester.runpytest_subprocess("-n", "2")
    records_dir = record_pytester.path / "test-logs" / "run-records"
    files = list(records_dir.glob("*.json"))
    assert len(files) == 1
    record = _record(record_pytester)
    assert len(record["tests"]) == 3
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/framework/test_run_record.py -v`
Expected: collection error — `ModuleNotFoundError: No module named 'utils.run_record'`.

- [ ] **Step 3: Write the plugin**

Create `utils/run_record.py`:

```python
"""Pytest plugin: per-run outcome recorder for durable flake history.

Records every test's final outcome for the session — nodeid, outcome
(``passed | failed | xfailed | xpassed | skipped``), reruns used, quarantine
state — and writes ``test-logs/run-records/run-record-<browser>.json`` at
session end. ``test-logs/`` is volume-mounted in docker compose, so the file
lands on the runner without new plumbing.

CI-only, like the v1 retry policy: inert unless ``GITHUB_RUN_ID`` is set —
local runs write nothing. xdist-aware exactly like ``utils/flaky_summary.py``:
workers' reports are forwarded to the controller and only the controller
writes (guard on ``workerinput``). Quarantine state arrives via the
``quarantine_expires`` user property stamped by ``utils/quarantine.py`` —
user properties are serialized into reports and survive the worker hop.
"""

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

RECORDS_DIR = Path("test-logs/run-records")

_outcomes: dict[str, str] = {}
_reruns: dict[str, int] = {}
_quarantine_expires: dict[str, str] = {}


def _enabled() -> bool:
    """Record only in CI — mirrors v1's CI-only retry policy."""
    return bool(os.environ.get("GITHUB_RUN_ID"))


def pytest_configure() -> None:
    """Reset module state so repeated in-process runs start clean."""
    _outcomes.clear()
    _reruns.clear()
    _quarantine_expires.clear()


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Fold each phase report into the test's final outcome."""
    if not _enabled():
        return
    if report.outcome == "rerun":  # type: ignore[comparison-overlap]
        _reruns[report.nodeid] = _reruns.get(report.nodeid, 0) + 1
        return
    for name, value in report.user_properties:
        if name == "quarantine_expires":
            _quarantine_expires[report.nodeid] = str(value)
    outcome = _classify(report)
    # A failure in any phase (setup error, teardown error) is final; later
    # phases must not soften it back to passed/skipped.
    if outcome and _outcomes.get(report.nodeid) != "failed":
        _outcomes[report.nodeid] = outcome


def _classify(report: pytest.TestReport) -> str | None:
    """Map one phase report onto the run-record outcome vocabulary."""
    if report.failed:
        return "failed"
    if hasattr(report, "wasxfail"):
        return "xpassed" if report.passed else "xfailed"
    if report.when == "call" and report.passed:
        return "passed"
    if report.skipped:
        return "skipped"
    return None


def pytest_sessionfinish(session: pytest.Session) -> None:
    """Write the run record; controller only, CI only."""
    if not _enabled() or hasattr(session.config, "workerinput"):
        return
    if not _outcomes:
        return
    browser = _browser_name(session.config)
    tests: list[dict[str, Any]] = []
    for nodeid in sorted(_outcomes):
        entry: dict[str, Any] = {
            "nodeid": nodeid,
            "outcome": _outcomes[nodeid],
            "reruns": _reruns.get(nodeid, 0),
            "quarantined": nodeid in _quarantine_expires,
        }
        if nodeid in _quarantine_expires:
            entry["expires"] = _quarantine_expires[nodeid]
        tests.append(entry)
    record = {
        "schema": 1,
        "run_id": os.environ["GITHUB_RUN_ID"],
        "sha": os.environ.get("GITHUB_SHA", ""),
        "branch": os.environ.get("GITHUB_REF_NAME", ""),
        "browser": browser,
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tests": tests,
    }
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    out = RECORDS_DIR / f"run-record-{browser}.json"
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def _browser_name(config: pytest.Config) -> str:
    """First ``--browser`` value (pytest-playwright appends), or ``default``."""
    browsers = config.getoption("--browser", default=None) or []
    return str(browsers[0]) if browsers else "default"
```

Then modify `conftest.py` — the `pytest_plugins` block becomes:

```python
# pytest_plugins may only be declared in the rootdir conftest.
# - utils.flaky_summary: retry observability (pass-on-retry counting);
#   lives in its own module so pytester tests can load the exact source.
# - utils.quarantine: quarantine marker -> xfail(strict=False) conversion.
# - utils.run_record: CI-only per-run outcome recorder for flake history.
# - pytester: enables the pytester fixture for framework plugin tests.
pytest_plugins = [
    "utils.flaky_summary",
    "utils.quarantine",
    "utils.run_record",
    "pytester",
]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/framework/test_run_record.py -v`
Expected: 5 passed.

- [ ] **Step 5: Static checks**

Run: `ruff check utils/run_record.py tests/framework/test_run_record.py conftest.py && ruff format --check utils/run_record.py tests/framework/test_run_record.py && mypy utils/run_record.py`
Expected: no findings.

- [ ] **Step 6: Commit**

```bash
git add utils/run_record.py tests/framework/test_run_record.py conftest.py
git commit -m "feat: CI-only run-record plugin — per-test outcomes for flake history"
```

---

### Task 3: Analyzer core — load, merge, detect (`scripts/analyze_flake_history.py`)

**Files:**
- Create: `scripts/analyze_flake_history.py` (data model + `load_history` + `load_run_records` + `merge` + `analyze_runs` + `detect`; rendering and `main()` come in Task 4)
- Create: `tests/framework/test_flake_analysis.py`

**Interfaces:**
- Consumes: run-record JSON files from Task 2; `history.json` (schema in spec).
- Produces (Task 4 relies on these exact names):
  - constants `SCHEMA`, `KEEP_RUNS = 50`, `DETECT_WINDOW = 30`, `FRESH_WINDOW = 10`, `FAIL_STREAK = 3`, `MIN_RUNS_FOR_RATE = 10`, `FAIL_RATE_THRESHOLD = 0.05`, `RELEASE_STREAK = 10`, `EXPIRY_WARN_DAYS = 7`, `QUARANTINE_TTL_DAYS = 30`
  - `@dataclass BrowserStats(browser: str, total: int, incidents: list[dict[str, Any]], fail_count: int, fresh_bad: bool, fail_streak: int, release_streak_ok: bool)`
  - `@dataclass Report(quarantine: dict[str, list[BrowserStats]], release: list[str], failing: dict[str, list[str]], expiring: list[tuple[str, str]], gaps: list[str])` — all fields `field(default_factory=...)`
  - `load_history(path: Path) -> dict[str, Any]`
  - `load_run_records(records_dir: Path) -> list[dict[str, Any]]`
  - `merge(history: dict[str, Any], records: list[dict[str, Any]]) -> None`
  - `detect(history: dict[str, Any], quarantined_now: dict[str, str], today: dt.date) -> Report`

- [ ] **Step 1: Write the failing tests**

Create `tests/framework/test_flake_analysis.py`:

```python
"""Unit tests for the flake-history analyzer's threshold logic.

Plain in-memory tests over the pure functions of
``scripts/analyze_flake_history.py`` — no pytester, no CI, no filesystem
except where load_history's recovery behavior is the subject.
"""

import datetime as dt
import json
from pathlib import Path
from typing import Any

from scripts.analyze_flake_history import (
    KEEP_RUNS,
    detect,
    load_history,
    merge,
)

NODEID = "tests/app/test_x.py::test_y"
TODAY = dt.date(2026, 7, 9)


def _run(run_id: int, outcome: str = "passed", reruns: int = 0) -> dict[str, Any]:
    return {
        "run_id": str(run_id),
        "sha": "abc1234",
        "outcome": outcome,
        "reruns": reruns,
        "quarantined": False,
    }


def _clean(count: int, start: int = 0) -> list[dict[str, Any]]:
    return [_run(i) for i in range(start, start + count)]


def _incident(run_id: int) -> dict[str, Any]:
    return _run(run_id, outcome="passed", reruns=1)


def _fail(run_id: int) -> dict[str, Any]:
    return _run(run_id, outcome="failed")


def _xpass(run_id: int) -> dict[str, Any]:
    entry = _run(run_id, outcome="xpassed")
    entry["quarantined"] = True
    return entry


def _xfail(run_id: int) -> dict[str, Any]:
    entry = _run(run_id, outcome="xfailed")
    entry["quarantined"] = True
    return entry


def _history(
    runs: list[dict[str, Any]], browser: str = "chromium"
) -> dict[str, Any]:
    return {"schema": 1, "tests": {NODEID: {browser: runs}}}


def _two_browser_history(
    chromium: list[dict[str, Any]], firefox: list[dict[str, Any]]
) -> dict[str, Any]:
    return {"schema": 1, "tests": {NODEID: {"chromium": chromium, "firefox": firefox}}}


def _record(
    run_id: int, tests: list[dict[str, Any]], browser: str = "chromium"
) -> dict[str, Any]:
    return {
        "schema": 1,
        "run_id": str(run_id),
        "sha": "abc1234",
        "branch": "main",
        "browser": browser,
        "timestamp": "2026-07-09T12:00:00Z",
        "tests": tests,
    }


def _record_test(outcome: str = "passed", reruns: int = 0) -> dict[str, Any]:
    return {
        "nodeid": NODEID,
        "outcome": outcome,
        "reruns": reruns,
        "quarantined": False,
    }


# ── quarantine candidates ────────────────────────────────────────────────────


def test_two_recent_incidents_propose_quarantine() -> None:
    history = _history(_clean(8) + [_incident(8), _incident(9)])
    report = detect(history, {}, TODAY)
    assert NODEID in report.quarantine


def test_single_incident_is_not_enough() -> None:
    history = _history(_clean(9) + [_incident(9)])
    report = detect(history, {}, TODAY)
    assert report.quarantine == {}


def test_stale_incidents_self_clean() -> None:
    history = _history([_incident(0), _incident(1)] + _clean(15, start=2))
    report = detect(history, {}, TODAY)
    assert report.quarantine == {}


def test_fail_rate_branch_proposes() -> None:
    history = _history(_clean(9) + [_fail(9)] + _clean(9, start=10) + [_fail(19)])
    report = detect(history, {}, TODAY)
    assert NODEID in report.quarantine


def test_fail_rate_below_threshold_is_quiet() -> None:
    history = _history(_clean(29) + [_fail(29)])
    report = detect(history, {}, TODAY)
    assert report.quarantine == {}


def test_trailing_fail_streak_is_regression_not_flake() -> None:
    history = _history(_clean(10) + [_fail(10), _fail(11), _fail(12)])
    report = detect(history, {}, TODAY)
    assert report.quarantine == {}
    assert report.failing == {NODEID: ["chromium"]}


def test_currently_quarantined_test_is_never_proposed() -> None:
    history = _history(_clean(8) + [_incident(8), _incident(9)])
    report = detect(history, {NODEID: "2026-08-01"}, TODAY)
    assert report.quarantine == {}


# ── un-quarantine candidates ─────────────────────────────────────────────────


def test_release_after_ten_consecutive_xpass() -> None:
    history = _history([_xpass(i) for i in range(10)])
    report = detect(history, {NODEID: "2026-08-01"}, TODAY)
    assert report.release == [NODEID]


def test_release_needs_the_full_streak() -> None:
    history = _history([_xfail(0)] + [_xpass(i) for i in range(1, 10)])
    report = detect(history, {NODEID: "2026-08-01"}, TODAY)
    assert report.release == []


def test_release_requires_every_browser_clean() -> None:
    dirty = [_xpass(i) for i in range(9)] + [_xfail(9)]
    history = _two_browser_history([_xpass(i) for i in range(10)], dirty)
    report = detect(history, {NODEID: "2026-08-01"}, TODAY)
    assert report.release == []


# ── expiring markers ─────────────────────────────────────────────────────────


def test_marker_expiring_within_week_is_listed() -> None:
    history = _history([_xpass(0)])
    report = detect(history, {NODEID: "2026-07-12"}, TODAY)
    assert report.expiring == [(NODEID, "2026-07-12")]


def test_far_expiry_is_not_listed() -> None:
    history = _history([_xpass(0)])
    report = detect(history, {NODEID: "2026-09-01"}, TODAY)
    assert report.expiring == []


# ── merge ────────────────────────────────────────────────────────────────────


def test_merge_appends_new_run() -> None:
    history = _history(_clean(3))
    merge(history, [_record(99, [_record_test()])])
    runs = history["tests"][NODEID]["chromium"]
    assert len(runs) == 4
    assert runs[-1]["run_id"] == "99"


def test_merge_windows_to_keep_runs() -> None:
    history = _history(_clean(KEEP_RUNS))
    merge(history, [_record(999, [_record_test()])])
    runs = history["tests"][NODEID]["chromium"]
    assert len(runs) == KEEP_RUNS
    assert runs[-1]["run_id"] == "999"


def test_merge_is_idempotent_per_run_id() -> None:
    history = _history(_clean(3))
    record = _record(99, [_record_test()])
    merge(history, [record])
    merge(history, [record])
    assert len(history["tests"][NODEID]["chromium"]) == 4


# ── history loading / recovery ───────────────────────────────────────────────


def test_missing_history_starts_fresh(tmp_path: Path) -> None:
    history = load_history(tmp_path / "absent.json")
    assert history == {"schema": 1, "tests": {}}


def test_corrupt_history_starts_fresh(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    path.write_text("{not json")
    history = load_history(path)
    assert history == {"schema": 1, "tests": {}}


def test_schema_mismatch_starts_fresh(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    path.write_text(json.dumps({"schema": 99, "tests": {NODEID: {}}}))
    history = load_history(path)
    assert history == {"schema": 1, "tests": {}}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/framework/test_flake_analysis.py -v`
Expected: collection error — `ModuleNotFoundError: No module named 'scripts.analyze_flake_history'`.

- [ ] **Step 3: Write the analyzer core**

Create `scripts/analyze_flake_history.py`:

```python
#!/usr/bin/env python3
"""Merge run records into flake history and propose (un-)quarantine candidates.

Runs in the ``publish-report`` CI job on main-branch pushes. Reads the
durable history from the gh-pages checkout, folds in the current run's
per-browser run records (written by ``utils/run_record.py``), applies the
detection thresholds from the v2 design spec, and writes two files into the
publish tree:

- ``history.json``  — updated durable history (last 50 runs per test/browser)
- ``candidates.md`` — human report: quarantine / un-quarantine candidates,
  expiring markers, deterministic failures, data gaps

The rendered markdown is also printed to stdout so the workflow can append
it to ``$GITHUB_STEP_SUMMARY``. The analyzer proposes; it never edits test
code and never fails the build (the workflow step uses continue-on-error).
Stdlib-only: it runs on the bare runner without installing dependencies.
"""

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA = 1
KEEP_RUNS = 50  # stored history window per (nodeid, browser)
DETECT_WINDOW = 30  # runs scanned for incidents / fail rate
FRESH_WINDOW = 10  # the most recent bad event must fall in this window
FAIL_STREAK = 3  # this many trailing fails = regression, not flake
MIN_RUNS_FOR_RATE = 10
FAIL_RATE_THRESHOLD = 0.05
RELEASE_STREAK = 10  # consecutive XPASS runs to propose un-quarantine
EXPIRY_WARN_DAYS = 7
QUARANTINE_TTL_DAYS = 30  # horizon for the ready-to-paste marker


@dataclass
class BrowserStats:
    """Detection inputs computed for one (nodeid, browser) history key."""

    browser: str
    total: int
    incidents: list[dict[str, Any]]
    fail_count: int
    fresh_bad: bool
    fail_streak: int
    release_streak_ok: bool


@dataclass
class Report:
    """Everything ``candidates.md`` needs, grouped by section."""

    quarantine: dict[str, list[BrowserStats]] = field(default_factory=dict)
    release: list[str] = field(default_factory=list)
    failing: dict[str, list[str]] = field(default_factory=dict)
    expiring: list[tuple[str, str]] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)


def _fresh_history() -> dict[str, Any]:
    return {"schema": SCHEMA, "tests": {}}


def load_history(path: Path) -> dict[str, Any]:
    """Load history; corrupt or schema-mismatched files start fresh (warn).

    History is derived data — the gh-pages git log retains old versions, so
    recovery by reset is safe and keeps the pipeline running.
    """
    if not path.exists():
        return _fresh_history()
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(f"warning: corrupt history at {path}; starting fresh", file=sys.stderr)
        return _fresh_history()
    if data.get("schema") != SCHEMA or not isinstance(data.get("tests"), dict):
        print(
            f"warning: unexpected history schema at {path}; starting fresh",
            file=sys.stderr,
        )
        return _fresh_history()
    return data


def load_run_records(records_dir: Path) -> list[dict[str, Any]]:
    """Load every readable run-record file; skip unreadable ones with a warning."""
    records: list[dict[str, Any]] = []
    for record_path in sorted(records_dir.glob("run-record-*.json")):
        try:
            record: dict[str, Any] = json.loads(record_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"warning: skipping corrupt {record_path}", file=sys.stderr)
            continue
        if record.get("schema") != SCHEMA:
            print(f"warning: skipping schema-mismatched {record_path}", file=sys.stderr)
            continue
        records.append(record)
    return records


def merge(history: dict[str, Any], records: list[dict[str, Any]]) -> None:
    """Fold run records into history, windowed to KEEP_RUNS per key.

    Idempotent per run_id: re-running the analyzer over the same artifacts
    (workflow re-run) must not duplicate entries.
    """
    for record in records:
        browser = record["browser"]
        for test in record["tests"]:
            runs: list[dict[str, Any]] = (
                history["tests"]
                .setdefault(test["nodeid"], {})
                .setdefault(browser, [])
            )
            if any(run["run_id"] == record["run_id"] for run in runs):
                continue
            runs.append(
                {
                    "run_id": record["run_id"],
                    "sha": record["sha"],
                    "outcome": test["outcome"],
                    "reruns": test["reruns"],
                    "quarantined": test.get("quarantined", False),
                }
            )
            del runs[:-KEEP_RUNS]


def _is_incident(run: dict[str, Any]) -> bool:
    """v1's pass-on-retry: same commit failed then passed."""
    return run["reruns"] > 0 and run["outcome"] == "passed"


def _is_bad(run: dict[str, Any]) -> bool:
    return _is_incident(run) or run["outcome"] == "failed"


def analyze_runs(runs: list[dict[str, Any]], browser: str) -> BrowserStats:
    """Compute every detection input for one (nodeid, browser) key."""
    window = runs[-DETECT_WINDOW:]
    incidents = [run for run in window if _is_incident(run)]
    fail_count = sum(1 for run in window if run["outcome"] == "failed")
    fresh_bad = any(_is_bad(run) for run in runs[-FRESH_WINDOW:])
    fail_streak = 0
    for run in reversed(runs):
        if run["outcome"] != "failed":
            break
        fail_streak += 1
    tail = runs[-RELEASE_STREAK:]
    release_streak_ok = len(tail) == RELEASE_STREAK and all(
        run["outcome"] == "xpassed" and run["reruns"] == 0 for run in tail
    )
    return BrowserStats(
        browser=browser,
        total=len(window),
        incidents=incidents,
        fail_count=fail_count,
        fresh_bad=fresh_bad,
        fail_streak=fail_streak,
        release_streak_ok=release_streak_ok,
    )


def _is_quarantine_trigger(stats: BrowserStats) -> bool:
    """Spec thresholds: (≥2 incidents OR fail rate ≥5% over ≥10 runs), fresh,
    and not a deterministic regression."""
    if not stats.fresh_bad or stats.fail_streak >= FAIL_STREAK:
        return False
    if len(stats.incidents) >= 2:
        return True
    return (
        stats.total >= MIN_RUNS_FOR_RATE
        and stats.fail_count / stats.total >= FAIL_RATE_THRESHOLD
    )


def detect(
    history: dict[str, Any], quarantined_now: dict[str, str], today: dt.date
) -> Report:
    """Apply thresholds per (nodeid, browser); aggregate whole-test verdicts.

    ``quarantined_now`` maps nodeid -> expires for tests quarantined in the
    freshest run records (the marker is whole-test, so quarantine state and
    release decisions are whole-test too; evidence stays per-browser).
    """
    report = Report()
    for nodeid in sorted(history["tests"]):
        browsers = history["tests"][nodeid]
        stats = [
            analyze_runs(runs, browser) for browser, runs in sorted(browsers.items())
        ]
        failing_browsers = [s.browser for s in stats if s.fail_streak >= FAIL_STREAK]
        if failing_browsers:
            report.failing[nodeid] = failing_browsers
        if nodeid in quarantined_now:
            if stats and all(s.release_streak_ok for s in stats):
                report.release.append(nodeid)
        elif any(_is_quarantine_trigger(s) for s in stats):
            report.quarantine[nodeid] = stats
    warn_horizon = today + dt.timedelta(days=EXPIRY_WARN_DAYS)
    for nodeid, expires_raw in sorted(quarantined_now.items()):
        if dt.date.fromisoformat(expires_raw) <= warn_horizon:
            report.expiring.append((nodeid, expires_raw))
    return report
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/framework/test_flake_analysis.py -v`
Expected: 18 passed.

- [ ] **Step 5: Static checks**

Run: `ruff check scripts/analyze_flake_history.py tests/framework/test_flake_analysis.py && ruff format --check scripts/analyze_flake_history.py tests/framework/test_flake_analysis.py && mypy scripts/analyze_flake_history.py`
Expected: no findings.

- [ ] **Step 6: Commit**

```bash
git add scripts/analyze_flake_history.py tests/framework/test_flake_analysis.py
git commit -m "feat: flake-history analyzer core — merge run records, threshold detection"
```

---

### Task 4: Analyzer report rendering + CLI (`render_markdown`, `main`)

**Files:**
- Modify: `scripts/analyze_flake_history.py` (append rendering + `main()`)
- Modify: `tests/framework/test_flake_analysis.py` (append rendering/CLI tests)

**Interfaces:**
- Consumes: `Report`, `BrowserStats`, `detect`, `merge`, `load_history`, `load_run_records`, constants — all from Task 3, exact names above.
- Produces: `render_markdown(report: Report, repo: str, today: dt.date, meta: str) -> str` and `main(argv: list[str] | None = None) -> int` with CLI flags `--history-file`, `--run-records-dir`, `--output-dir`, `--repo`, `--browsers`. Task 5's workflow step calls this CLI.

- [ ] **Step 1: Write the failing tests**

Modify `tests/framework/test_flake_analysis.py`: add `Report`, `main`, `render_markdown` to the existing single `from scripts.analyze_flake_history import (...)` block (one import statement, alphabetized), and add `import pytest` to the imports (needed for the `capsys` type below). Then append these tests:

```python
# ── rendering ────────────────────────────────────────────────────────────────


def test_healthy_report_says_so_explicitly() -> None:
    md = render_markdown(Report(), "owner/repo", TODAY, "Analyzed 0 run record(s)")
    assert "No candidates. Suite is healthy." in md


def test_candidate_includes_paste_ready_marker_with_computed_expiry() -> None:
    history = _history(_clean(8) + [_incident(8), _incident(9)])
    report = detect(history, {}, TODAY)
    md = render_markdown(report, "owner/repo", TODAY, "meta")
    assert '@pytest.mark.quarantine(reason="TICKET-???' in md
    assert 'expires="2026-08-08"' in md


def test_candidate_evidence_links_incident_runs() -> None:
    history = _history(_clean(8) + [_incident(8), _incident(9)])
    report = detect(history, {}, TODAY)
    md = render_markdown(report, "owner/repo", TODAY, "meta")
    assert "https://github.com/owner/repo/actions/runs/9" in md


def test_clean_browser_shown_alongside_dirty_one() -> None:
    dirty = _clean(8) + [_incident(8), _incident(9)]
    history = _two_browser_history(dirty, _clean(10))
    report = detect(history, {}, TODAY)
    md = render_markdown(report, "owner/repo", TODAY, "meta")
    assert "clean (10/10)" in md


def test_failing_not_flaky_section_renders() -> None:
    history = _history(_clean(10) + [_fail(10), _fail(11), _fail(12)])
    report = detect(history, {}, TODAY)
    md = render_markdown(report, "owner/repo", TODAY, "meta")
    assert "Failing, not flaky" in md
    assert "No candidates. Suite is healthy." not in md


def test_expiring_section_renders() -> None:
    history = _history([_xpass(0)])
    report = detect(history, {NODEID: "2026-07-12"}, TODAY)
    md = render_markdown(report, "owner/repo", TODAY, "meta")
    assert "Expiring soon" in md
    assert "2026-07-12" in md


# ── CLI end-to-end ───────────────────────────────────────────────────────────


def test_main_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    records_dir = tmp_path / "records"
    records_dir.mkdir()
    record = _record(99, [_record_test()])
    (records_dir / "run-record-chromium.json").write_text(json.dumps(record))
    out_dir = tmp_path / "publish"
    exit_code = main(
        [
            "--history-file",
            str(tmp_path / "gh-pages" / "flake-history" / "history.json"),
            "--run-records-dir",
            str(records_dir),
            "--output-dir",
            str(out_dir),
            "--repo",
            "owner/repo",
            "--browsers",
            "chromium,firefox,webkit",
        ]
    )
    assert exit_code == 0
    written = json.loads((out_dir / "history.json").read_text())
    assert NODEID in written["tests"]
    md = (out_dir / "candidates.md").read_text()
    assert "no run record for firefox" in md
    assert "no run record for webkit" in md
    assert capsys.readouterr().out == md
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/framework/test_flake_analysis.py -v`
Expected: ImportError — `cannot import name 'render_markdown'`.

- [ ] **Step 3: Implement rendering + main**

Append to `scripts/analyze_flake_history.py`:

```python
def render_markdown(
    report: Report, repo: str, today: dt.date, meta: str
) -> str:
    """Render candidates.md — one reader (weekly review), one job (marker PR).

    Regenerated whole from state every run; deterministic ordering (sorted by
    nodeid, done in ``detect``) so gh-pages diffs show state changes, not row
    shuffling.
    """
    lines = [f"# Flake candidates — {today.isoformat()}", "", meta, ""]
    suggested_expiry = (today + dt.timedelta(days=QUARANTINE_TTL_DAYS)).isoformat()
    if report.quarantine:
        lines.append(f"## Quarantine candidates ({len(report.quarantine)})")
        for nodeid, stats in report.quarantine.items():
            lines += ["", f"### `{nodeid}`", "", "| browser | evidence |", "|---|---|"]
            lines += [f"| {s.browser} | {_evidence(s, repo)} |" for s in stats]
            lines += [
                "",
                "Suggested marker (fill in the ticket):",
                "",
                "```python",
                (
                    '@pytest.mark.quarantine(reason="TICKET-???: <root cause>", '
                    f'expires="{suggested_expiry}")'
                ),
                "```",
            ]
        lines.append("")
    if report.release:
        lines.append(f"## Un-quarantine candidates ({len(report.release)})")
        lines.append("")
        lines += [
            (
                f"- `{nodeid}` — last {RELEASE_STREAK} runs XPASS on every recorded "
                "browser. Action: remove the `quarantine` marker."
            )
            for nodeid in report.release
        ]
        lines.append("")
    if report.expiring:
        lines.append(f"## Expiring soon ({len(report.expiring)})")
        lines.append("")
        lines += [
            f"- `{nodeid}` — quarantine expires **{expires}**; fix or extend "
            "before it aborts CI at collection."
            for nodeid, expires in report.expiring
        ]
        lines.append("")
    if report.failing:
        lines.append(
            f"## Failing, not flaky ({len(report.failing)}) — fix, don't quarantine"
        )
        lines.append("")
        lines += [
            f"- `{nodeid}` — deterministic fail streak on: {', '.join(browsers)}"
            for nodeid, browsers in sorted(report.failing.items())
        ]
        lines.append("")
    if report.gaps:
        lines.append("## Data gaps")
        lines.append("")
        lines += [f"- {gap}" for gap in report.gaps]
        lines.append("")
    if not (report.quarantine or report.release or report.expiring or report.failing):
        lines += ["**No candidates. Suite is healthy.**", ""]
    return "\n".join(lines)


def _evidence(stats: BrowserStats, repo: str) -> str:
    """One evidence cell: incident links + fail count, or an explicit clean."""
    if not stats.incidents and stats.fail_count == 0:
        return f"clean ({stats.total}/{stats.total})"
    parts: list[str] = []
    if stats.incidents:
        links = ", ".join(
            f"[run {run['run_id']}]"
            f"(https://github.com/{repo}/actions/runs/{run['run_id']})"
            for run in stats.incidents
        )
        parts.append(
            f"{len(stats.incidents)} flake incident(s) in last "
            f"{stats.total} runs: {links}"
        )
    if stats.fail_count:
        parts.append(f"{stats.fail_count} fail(s) in last {stats.total} runs")
    return "; ".join(parts)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the publish-report workflow step."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-file", required=True, type=Path)
    parser.add_argument("--run-records-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo", required=True, help="owner/repo for run links")
    parser.add_argument(
        "--browsers", required=True, help="comma-separated expected browsers"
    )
    args = parser.parse_args(argv)

    today = dt.date.today()
    history = load_history(args.history_file)
    records = load_run_records(args.run_records_dir)
    quarantined_now: dict[str, str] = {
        test["nodeid"]: test["expires"]
        for record in records
        for test in record["tests"]
        if test.get("quarantined") and test.get("expires")
    }
    merge(history, records)
    report = detect(history, quarantined_now, today)

    expected = {browser for browser in args.browsers.split(",") if browser}
    found = {record["browser"] for record in records}
    report.gaps = sorted(f"no run record for {browser}" for browser in expected - found)

    run_ids = sorted({record["run_id"] for record in records})
    meta = (
        f"Analyzed {len(records)} run record(s) from run(s) "
        f"{', '.join(run_ids) or '—'} · {len(history['tests'])} test(s) tracked"
    )
    markdown = render_markdown(report, args.repo, today, meta)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "history.json").write_text(
        json.dumps(history, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "candidates.md").write_text(markdown, encoding="utf-8")
    sys.stdout.write(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/framework/test_flake_analysis.py -v`
Expected: 25 passed.

- [ ] **Step 5: Static checks**

Run: `ruff check scripts/analyze_flake_history.py tests/framework/test_flake_analysis.py && ruff format --check scripts/analyze_flake_history.py tests/framework/test_flake_analysis.py && mypy scripts/analyze_flake_history.py`
Expected: no findings.

- [ ] **Step 6: Commit**

```bash
git add scripts/analyze_flake_history.py tests/framework/test_flake_analysis.py
git commit -m "feat: candidates.md rendering and analyzer CLI"
```

---

### Task 5: CI wiring + live quarantine demo

**Files:**
- Modify: `.github/workflows/tests.yml` (env bridging in the tests job; run-record artifact; analyzer step in publish-report)
- Create: `tests/framework/test_quarantine_demo.py`

**Interfaces:**
- Consumes: the `run-record-<browser>.json` files (Task 2) and the analyzer CLI (Task 4).
- Produces: `flake-history/history.json` + `flake-history/candidates.md` on gh-pages; candidates report in the run's step summary.

**Spec deviation (deliberate, document in the commit):** the spec reuses the `test-artifacts-<browser>` artifact for run records, but that artifact also contains Playwright traces (potentially hundreds of MB) — downloading it into publish-report just for one JSON is wasteful. Instead the tests job uploads a dedicated tiny `run-record-<browser>` artifact.

- [ ] **Step 1: Add the demo test**

Create `tests/framework/test_quarantine_demo.py`:

```python
"""Live demo of the quarantine pipeline (analogous to ``test_flaky_demo``).

Deliberately fails on every run: the quarantine marker must convert the
failure to XFAIL so the suite stays green, and the CI run record must carry
``quarantined: true`` with the expiry date — proving the contain + remember
stages end-to-end. The far-future ``expires`` deliberately ignores the
~30-day hygiene rule: this is permanent infrastructure demonstration, not a
real quarantined flake.
"""

import pytest


@pytest.mark.quarantine(
    reason="DEMO: permanent proof that quarantined failures never block",
    expires="2099-01-01",
)
def test_quarantine_demo_shielded_failure() -> None:
    raise AssertionError("deliberate failure absorbed by the quarantine shield")
```

- [ ] **Step 2: Verify the demo is shielded in the real suite**

Run: `pytest tests/framework/test_quarantine_demo.py -v`
Expected: `1 xfailed`, exit code 0.

- [ ] **Step 3: Bridge CI env into the container**

In `.github/workflows/tests.yml`, the `Run tests` step (around line 69) becomes:

```yaml
      - name: Run tests (${{ matrix.browser }})
        run: >-
          docker compose run --rm
          -e GITHUB_STEP_SUMMARY=/work/test-logs/flaky-summary.md
          -e GITHUB_RUN_ID -e GITHUB_SHA -e GITHUB_REF_NAME
          tests --browser=${{ matrix.browser }}
          --reruns=1 --only-rerun "TimeoutError|net::ERR|NS_ERROR_|Could not connect"
```

(`-e VAR` with no value passes the runner's own env through — same bridging v1 needed for `GITHUB_STEP_SUMMARY`; docker compose does not inherit runner env otherwise.)

- [ ] **Step 4: Upload the run record as its own artifact**

In the tests job, after the `Upload traces and logs` step, add:

```yaml
      - name: Upload run record
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: run-record-${{ matrix.browser }}
          path: test-logs/run-records/
          if-no-files-found: ignore
          retention-days: 14
```

- [ ] **Step 5: Wire the analyzer into publish-report**

In the `publish-report` job:

(a) Add a repo checkout as the FIRST step (the job currently never checks out the repo; the analyzer script must come from the tested ref). `path: repo` keeps all existing relative paths untouched:

```yaml
      - name: Checkout repo (for the analyzer script)
        uses: actions/checkout@v6
        with:
          path: repo
```

(b) After the existing `Download Allure results from all browsers` step, add:

```yaml
      - name: Download run records from all browsers
        uses: actions/download-artifact@v4
        with:
          pattern: run-record-*
          merge-multiple: true
          path: run-records
```

(c) Between `Drop stray .git dirs from publish assets` and `Deploy to gh-pages`, add:

```yaml
      # The analyzer proposes; it never fails the build. allure-report-action
      # has already copied the previous gh-pages content (including last run's
      # flake-history/) into allure-history, so on analyzer failure the stale
      # copy survives instead of vanishing.
      - name: Analyze flake history
        continue-on-error: true
        run: |
          python3 repo/scripts/analyze_flake_history.py \
            --history-file gh-pages/flake-history/history.json \
            --run-records-dir run-records \
            --output-dir allure-history/flake-history \
            --repo "${{ github.repository }}" \
            --browsers chromium,firefox,webkit \
            >> "$GITHUB_STEP_SUMMARY"
```

- [ ] **Step 6: Sanity-check the workflow file**

Run: `python3 -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('.github/workflows/tests.yml').read_text()); print('yaml ok')"`
Expected: `yaml ok`. (If `actionlint` is installed, run `actionlint .github/workflows/tests.yml` too.)

- [ ] **Step 7: Run the full framework layer as regression**

Run: `pytest tests/framework -v`
Expected: all pass; exactly 1 xfailed (the demo); 0 failed. Note: `test_flaky_demo.py` tests skip without `--reruns` — skips are expected.

- [ ] **Step 8: Static checks**

Run: `ruff check tests/framework/test_quarantine_demo.py && ruff format --check tests/framework/test_quarantine_demo.py`
Expected: no findings.

- [ ] **Step 9: Commit**

```bash
git add .github/workflows/tests.yml tests/framework/test_quarantine_demo.py
git commit -m "ci: wire flake history pipeline — env bridging, run-record artifact, analyzer in publish-report"
```

---

## Post-merge verification (manual, after PR merges to main)

Not executable now — record as follow-ups:
1. First main push: check the `publish-report` job log for the analyzer step; step summary should show "No candidates" (or the demo in history).
2. `https://github.com/summerduck/fintech-playwright-quality/blob/gh-pages/flake-history/candidates.md` renders.
3. `history.json` on gh-pages contains the demo test with `quarantined: true` for all three browsers.
