"""Predefined test data for The Internet application.

Pure constants only — no environment access, no side effects.
Credentials are resolved at runtime via ``TheInternetSettings``
in ``config/settings.py``.
"""

from config.data.models import User


class TheInternetUser:
    """Non-secret user identities for The Internet application.

    Passwords are intentionally omitted — they are injected at runtime
    from environment variables via ``TheInternetSettings.as_user()``.
    """

    VALID = User(username="admin")
