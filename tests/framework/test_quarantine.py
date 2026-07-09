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
