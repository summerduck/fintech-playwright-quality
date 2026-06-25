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

    def _masked_number(self) -> str:
        """Return the card number with all but the last 4 digits masked.

        This is the single source of truth for how a PAN appears in any
        string/representation of a Card, so it must never expose the full
        number. Used by both __str__ and __repr__.
        """
        total_digits = sum(char.isdigit() for char in self.number)
        visible = 4 if total_digits > 4 else 0
        digits_from_end = 0
        masked: list[str] = []
        for char in reversed(self.number):
            if not char.isdigit():
                masked.append(char)
                continue
            digits_from_end += 1
            masked.append(char if digits_from_end <= visible else "*")
        return "".join(reversed(masked))

    def __str__(self) -> str:
        return self._masked_number()

    def __repr__(self) -> str:
        return (
            f"Card(number={self._masked_number()}, name={self.name!r}, "
            f"cvc=***, expiration_date={self.expiration_date!r}, "
            f"zip_code={self.zip_code!r}, requires_3ds={self.requires_3ds})"
        )
