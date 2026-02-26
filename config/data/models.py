"""Shared test-data models used across all apps."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Immutable user credentials for authentication tests.

    Attributes:
        username: Login username.
        password: Login password.
    """

    username: str
    password: str = ""

    def __str__(self) -> str:
        return self.username
