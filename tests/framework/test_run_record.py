"""Pytester tests for the run-record plugin (``utils/run_record.py``).

The quarantined-entry test simulates the quarantine plugin's output (an
xfail marker plus a ``quarantine_expires`` user property) instead of loading
both plugins into one sandbox conftest — two modules defining the same hooks
cannot be concatenated. The real two-plugin integration is exercised by the
demo test in the live suite (``test_quarantine_demo.py``).
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
