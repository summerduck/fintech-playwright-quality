"""Deterministic flaky demo: proves the retry pipeline end to end.

Runs in every CI run so the published Allure report always contains one
retried, flaky-marked test. The flaky-summary plugin counts it on its own
``flaky (demo)`` line, never in the real flaky total. Deterministic — the
flake reproduces 100% of the time; no randomness.
"""

import allure
import pytest


@pytest.mark.flaky_demo
@allure.title("Flaky retry demo — deterministic fail-then-pass")
@allure.description(
    "Intentionally fails its first attempt with a Playwright TimeoutError "
    "and passes on the retry. Demonstrates the CI retry policy and "
    "pass-on-retry reporting; it is not a test of the application. "
    "Skips locally, where retries are disabled (--reruns=0)."
)
def test_deterministic_flaky_demo(flaky_simulation: int) -> None:
    """Passes only on attempt 2; the fixture raises on attempt 1."""
    assert flaky_simulation > 1
