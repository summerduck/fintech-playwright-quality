"""Unit tests for the JUnit false-green gate."""

import pytest

from utils.junit_gate import evaluate_gate


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
    ],
)
def test_evaluate_gate(counts, expected_ok, reason_contains):
    ok, reason = evaluate_gate(counts)
    assert ok is expected_ok
    assert reason_contains in reason
