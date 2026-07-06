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
    if report.outcome == "rerun":  # type: ignore[comparison-overlap]
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
