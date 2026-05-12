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


@dataclass(frozen=True)
class Card:
    """Immutable payment card data for card flow tests.

    Attributes:
        number: Card number (space-separated groups, e.g. '4242 4242 4242 4242').
        name: Cardholder name.
        cvc: Card verification code.
        expiration_date: Expiry in MM/YY format.
        zip_code: Billing postal code.
        requires_3ds: Whether this card triggers 3D Secure authentication.
    """

    number: str
    name: str
    cvc: str
    expiration_date: str
    zip_code: str
    requires_3ds: bool = False

    def __str__(self) -> str:
        return self.number
