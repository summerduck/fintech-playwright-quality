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

import sys
import xml.etree.ElementTree as ET  # nosec B405


def parse_junit(path: str) -> dict[str, int]:
    """Sum test counts across every <testsuite> in a pytest JUnit XML file.

    Returns keys: tests, failures, errors, skipped, passed.
    `passed` is derived: tests - failures - errors - skipped.
    Raises OSError (missing file) / ET.ParseError (malformed) to the caller.
    """
    # Trusted source (pytest self-generates junit.xml in-job): stdlib etree is
    # fine. Switch to defusedxml if this ever parses an untrusted report.
    root = ET.parse(path).getroot()  # nosec B314  # <testsuites> wrapper or bare <testsuite>
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for suite in root.iter("testsuite"):
        for key in totals:
            totals[key] += int(suite.get(key, 0))
    totals["passed"] = (
        totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
    )
    return totals


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


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: junit_gate.py <junit.xml>", file=sys.stderr)
        return 2

    path = argv[0]
    try:
        counts = parse_junit(path)
    except (OSError, ET.ParseError) as exc:
        print(
            f"❌ gate FAIL (false green): no junit report — run produced no "
            f"result ({exc})",
            file=sys.stderr,
        )
        return 1

    print(
        f"report: {counts['tests']} collected · {counts['passed']} passed · "
        f"{counts['failures']} failed · {counts['errors']} errors · "
        f"{counts['skipped']} skipped"
    )
    ok, reason = evaluate_gate(counts)
    if ok:
        print(f"✅ gate PASS: {reason}")
        return 0
    print(f"❌ gate FAIL (false green): {reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
