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
