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
