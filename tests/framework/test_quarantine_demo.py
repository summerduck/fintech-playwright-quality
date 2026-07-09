"""Live demo of the quarantine pipeline (analogous to ``test_flaky_demo``).

Deliberately fails on every run: the quarantine marker must convert the
failure to XFAIL so the suite stays green, and the CI run record must carry
``quarantined: true`` with the expiry date — proving the contain + remember
stages end-to-end. The far-future ``expires`` deliberately ignores the
~30-day hygiene rule: this is permanent infrastructure demonstration, not a
real quarantined flake.
"""

import pytest


@pytest.mark.quarantine(
    reason="DEMO: permanent proof that quarantined failures never block",
    expires="2099-01-01",
)
def test_quarantine_demo_shielded_failure() -> None:
    raise AssertionError("deliberate failure absorbed by the quarantine shield")
