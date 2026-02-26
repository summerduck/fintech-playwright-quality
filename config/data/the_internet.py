"""Predefined test data for The Internet application.

Credentials are resolved from environment variables at call time.
``load_dotenv()`` runs in ``pytest_configure`` before test collection,
so env vars are available when these functions are called.
"""

import os

from config.data.models import User


class TheInternetUser:
    """User factories for The Internet application.

    Each method resolves credentials from environment variables,
    keeping secrets out of source code.
    """

    @staticmethod
    def valid() -> User:
        """Valid Basic Auth user from THE_INTERNET_USERNAME / PASSWORD."""
        return User(
            username=os.environ["THE_INTERNET_USERNAME"],
            password=os.environ["THE_INTERNET_PASSWORD"],
        )
