"""App-level settings resolved from environment variables.

Each app gets its own ``BaseSettings`` subclass with an ``env_prefix``
that namespaces all variables (e.g. ``THE_INTERNET_USERNAME``).

``pydantic-settings`` reads ``.env`` files automatically and validates
types at instantiation time — missing variables produce a clear error
before any test runs.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

from config.data.models import User


class TheInternetSettings(BaseSettings):
    """Credentials for The Internet application.

    Reads ``THE_INTERNET_USERNAME`` and ``THE_INTERNET_PASSWORD``
    from environment variables or ``.env`` file.
    """

    model_config = SettingsConfigDict(
        env_prefix="THE_INTERNET_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    username: str
    password: str

    def as_user(self) -> User:
        """Convert settings to a frozen User dataclass."""
        return User(username=self.username, password=self.password)
