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
