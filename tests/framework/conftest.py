"""Framework-layer pytest configuration.

Retry eligibility is a property of the test layer: only browser-driven e2e
tests fail on infra noise, so only they may retry. This layer's unit tests
fail on logic — a retry could only mask a bug — so every item is stamped
``flaky(reruns=0)``, which takes precedence over any CLI ``--reruns`` flag.
The ``flaky_demo``-marked test is exempt: it exists to prove the retry
pipeline and must stay retry-eligible.
"""

from pathlib import Path

import pytest

_FRAMEWORK_DIR = Path(__file__).parent


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Opt this layer out of retries, except the ``flaky_demo`` test.

    Collection hooks receive ALL collected items, not just this directory's
    — the path filter keeps the stamp from leaking onto the e2e suites.
    """
    for item in items:
        outside_layer = not item.path.is_relative_to(_FRAMEWORK_DIR)
        if outside_layer or item.get_closest_marker("flaky_demo"):
            continue
        item.add_marker(pytest.mark.flaky(reruns=0))
