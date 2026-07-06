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
    if report.outcome == "rerun":  # type: ignore[comparison-overlap]
        bucket = (
            _demo_rerun_nodeids if "flaky_demo" in report.keywords else _rerun_nodeids
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


def _summary_lines(flaky: list[str], demo: list[str], failed: list[str]) -> list[str]:
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
