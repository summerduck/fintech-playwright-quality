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

_DEMO_FAIL_THEN_PASS = """
import pytest


@pytest.mark.flaky_demo
def test_demo_recovers(request: pytest.FixtureRequest) -> None:
    assert getattr(request.node, "execution_count", 1) > 1
"""


@pytest.fixture
def flaky_pytester(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> pytest.Pytester:
    """A pytester sandbox whose conftest is the production plugin source.

    Drops ``GITHUB_STEP_SUMMARY`` so sandbox runs never append their fake
    results to the real CI step summary (pytester subprocesses inherit
    os.environ; in CI the variable points at the job's summary file).
    """
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
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


def test_xdist_mirrors_step_summary_exactly_once(
    flaky_pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Under xdist the worker that saw the rerun must not also write the file.

    ``pytest_terminal_summary`` runs on workers too — their terminal output
    is discarded, but a file append is not. Only the controller may mirror.
    """
    summary_file = tmp_path / "step_summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
    flaky_pytester.makepyfile(_FAIL_THEN_PASS)
    result = flaky_pytester.runpytest_subprocess("--reruns=1", "-n", "2")
    result.assert_outcomes(passed=1)
    assert summary_file.read_text().count("## Flaky test summary") == 1
