"""Pytest plugin: quarantine marker — run flaky tests without blocking merges.

Registered from the root ``conftest.py`` via ``pytest_plugins``. A test marked
``@pytest.mark.quarantine(reason=..., expires=...)`` is converted at
collection time to ``xfail(strict=False)``: failures become XFAIL, passes
become XPASS, and neither blocks the run. The marker in the test file IS the
quarantine list — ``git grep quarantine`` enumerates it.

Hygiene is enforced at collection:
- ``reason`` and ``expires`` (ISO date) are both required;
- an ``expires`` date in the past aborts the run with ``UsageError`` naming
  every expired test — fix or extend, never silent decay.

Side effect worth knowing: pytest-rerunfailures does not rerun xfailed tests,
so quarantined tests stop consuming the CI retry budget. The expiry date is
stamped onto ``item.user_properties`` so the run-record plugin
(``utils/run_record.py``) can report quarantine state without re-reading
markers — user properties travel with reports across xdist workers.
"""

import datetime as dt

import pytest

QUARANTINE_EXPIRES_PROPERTY = "quarantine_expires"


def pytest_configure(config: pytest.Config) -> None:
    """Register the marker so ``--strict-markers`` accepts it."""
    config.addinivalue_line(
        "markers",
        "quarantine(reason, expires): run but never block — converted to "
        "xfail(strict=False); an expired ISO 'expires' date aborts collection",
    )


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Convert quarantine markers to non-strict xfail; abort on invalid ones."""
    errors: list[str] = []
    today = dt.date.today()
    for item in items:
        marker = item.get_closest_marker("quarantine")
        if marker is None:
            continue
        problem = _apply_quarantine(item, marker, today)
        if problem:
            errors.append(problem)
    if errors:
        raise pytest.UsageError("\n".join(errors))


def _apply_quarantine(
    item: pytest.Item, marker: pytest.Mark, today: dt.date
) -> str | None:
    """Validate marker kwargs and add the xfail shield; return the error text."""
    reason = marker.kwargs.get("reason")
    expires_raw = marker.kwargs.get("expires")
    if not reason or not expires_raw:
        return f"{item.nodeid}: quarantine marker requires reason= and expires="
    try:
        expires = dt.date.fromisoformat(expires_raw)
    except (TypeError, ValueError):
        return (
            f"{item.nodeid}: quarantine expires= must be an ISO date "
            f"(YYYY-MM-DD), got {expires_raw!r}"
        )
    if expires < today:
        return (
            f"{item.nodeid}: quarantine expired on {expires_raw} "
            f"(reason: {reason}) — fix the test or extend the date"
        )
    item.add_marker(pytest.mark.xfail(reason=f"quarantined: {reason}", strict=False))
    item.user_properties.append((QUARANTINE_EXPIRES_PROPERTY, expires_raw))
    return None
