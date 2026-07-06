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
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

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


@pytest.fixture
def flaky_simulation(request: pytest.FixtureRequest) -> None:
    """Deterministically fail attempt 1 with an infra-shaped error.

    Keyed on ``request.node.execution_count`` (set by pytest-rerunfailures,
    starts at 1); the ``getattr`` default covers profiles that disable the
    plugin outright (mutmut runs ``-p no:rerunfailures``), where the option
    lookup below also falls back to 0 and the test skips. Raises Playwright
    ``TimeoutError`` so the failure matches the CI ``--only-rerun`` regex.
    """
    reruns: int = request.config.getoption("--reruns", default=0) or 0
    if reruns == 0:
        pytest.skip(
            "flaky demo is meaningful only with retries enabled "
            "(CI passes --reruns=1); skipping on retry-less runs"
        )
    if getattr(request.node, "execution_count", 1) == 1:
        raise PlaywrightTimeoutError(
            "simulated infrastructure flake: attempt 1 always times out"
        )
