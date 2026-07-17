#!/usr/bin/env python3
"""JUnit gate: judge a test run by its report, not the process exit code.

Usage:
    python3 utils/junit_gate.py test-results/junit.xml

Exit 0 -> run is trustworthy. Exit 1 -> false-green detected, fail the step.
Exit 2 -> usage error.

pytest can exit 0 while verifying nothing (every test skipped) or have its
non-zero code swallowed upstream (`|| true`, a container layer). Reading the
report closes that gap. See demos/false_green/ for the walkthrough.
"""


def evaluate_gate(counts: dict[str, int]) -> tuple[bool, str]:
    """Decide whether a run is trustworthy from its JUnit counts.

    Checks run specific -> general so the most specific cause wins the reason.
    `counts` keys: tests, passed, failures, errors, skipped.
    """
    if counts["tests"] == 0:
        return False, "no tests collected"
    if counts["failures"] > 0 or counts["errors"] > 0:
        return False, f"{counts['failures']} failures / {counts['errors']} errors"
    if counts["passed"] == 0:
        return False, "all tests skipped"
    return True, f"{counts['passed']} passed"
