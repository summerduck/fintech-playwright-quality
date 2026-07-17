"""Unit tests for the JUnit false-green gate."""

import xml.etree.ElementTree as ET

import pytest

from utils.junit_gate import evaluate_gate, main, parse_junit


@pytest.mark.unit
@pytest.mark.parametrize(
    "counts, expected_ok, reason_contains",
    [
        # healthy: real passes -> trustworthy
        (
            {"tests": 5, "passed": 5, "failures": 0, "errors": 0, "skipped": 0},
            True,
            "passed",
        ),
        # nothing collected -> false green
        (
            {"tests": 0, "passed": 0, "failures": 0, "errors": 0, "skipped": 0},
            False,
            "no tests collected",
        ),
        # everything skipped -> false green
        (
            {"tests": 3, "passed": 0, "failures": 0, "errors": 0, "skipped": 3},
            False,
            "all tests skipped",
        ),
        # real failures -> flagged (defense-in-depth)
        (
            {"tests": 5, "passed": 4, "failures": 1, "errors": 0, "skipped": 0},
            False,
            "failures",
        ),
        # collection/fixture errors -> flagged like failures
        (
            {"tests": 5, "passed": 4, "failures": 0, "errors": 1, "skipped": 0},
            False,
            "errors",
        ),
        # failures present AND passed==0 -> failure reason wins (specific first)
        (
            {"tests": 5, "passed": 0, "failures": 5, "errors": 0, "skipped": 0},
            False,
            "failures",
        ),
        # malformed: derived passed goes negative -> must still FAIL, not false-pass
        (
            {"tests": 1, "passed": -1, "failures": 0, "errors": 0, "skipped": 2},
            False,
            "skipped",
        ),
    ],
)
def test_evaluate_gate(counts, expected_ok, reason_contains):
    ok, reason = evaluate_gate(counts)
    assert ok is expected_ok
    assert reason_contains in reason


_TWO_SUITES = """<?xml version="1.0"?>
<testsuites>
  <testsuite tests="3" failures="1" errors="0" skipped="1"></testsuite>
  <testsuite tests="2" failures="0" errors="1" skipped="0"></testsuite>
</testsuites>
"""


@pytest.mark.unit
def test_parse_junit_sums_across_suites(tmp_path):
    xml_file = tmp_path / "junit.xml"
    xml_file.write_text(_TWO_SUITES)

    counts = parse_junit(str(xml_file))

    assert counts == {
        "tests": 5,
        "failures": 1,
        "errors": 1,
        "skipped": 1,
        "passed": 2,
    }


@pytest.mark.unit
def test_parse_junit_missing_file_raises(tmp_path):
    with pytest.raises(OSError):
        parse_junit(str(tmp_path / "does_not_exist.xml"))


@pytest.mark.unit
def test_parse_junit_malformed_raises(tmp_path):
    bad = tmp_path / "bad.xml"
    bad.write_text("<testsuite not closed")

    with pytest.raises(ET.ParseError):
        parse_junit(str(bad))


_HEALTHY = """<?xml version="1.0"?>
<testsuite tests="2" failures="0" errors="0" skipped="0"></testsuite>
"""


@pytest.mark.unit
def test_main_passes_on_healthy_report(tmp_path):
    xml_file = tmp_path / "junit.xml"
    xml_file.write_text(_HEALTHY)

    assert main([str(xml_file)]) == 0


@pytest.mark.unit
def test_main_fails_on_missing_report(tmp_path):
    assert main([str(tmp_path / "missing.xml")]) == 1


@pytest.mark.unit
def test_main_usage_error_on_bad_args():
    assert main([]) == 2
