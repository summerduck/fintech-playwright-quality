"""Unit tests for config.data.models.Card sensitive-data masking."""

import pytest

from config.data.models import Card


def _make_card(number: str, cvc: str = "987") -> Card:
    """Build a Card with non-sensitive defaults, overriding only what's tested."""
    return Card(
        number=number,
        name="Jenny Rosen",
        cvc=cvc,
        expiration_date="12/34",
        zip_code="55555",
    )


@pytest.mark.unit
class TestCardMasking:
    """Verify Card never exposes the full PAN or the CVC in any string form."""

    @pytest.mark.parametrize(
        ("number", "expected"),
        [
            pytest.param(
                "4242 4242 4242 4242", "**** **** **** 4242", id="visa-grouped"
            ),
            pytest.param("4242424242424242", "************4242", id="no-spaces"),
            pytest.param("3782 822463 10005", "**** ****** *0005", id="amex-uneven"),
            pytest.param("424", "***", id="short-masks-everything"),
            pytest.param("4242", "****", id="exactly-four-masks-everything"),
        ],
    )
    def test_str_shows_only_last_four_digits(self, number: str, expected: str) -> None:
        card = _make_card(number)
        assert str(card) == expected

    def test_str_never_contains_the_full_pan(self) -> None:
        card = _make_card("4242 4242 4242 4242")
        assert "4242 4242 4242" not in str(card)

    def test_repr_masks_the_pan(self) -> None:
        card = _make_card("4242 4242 4242 4242")
        assert "4242 4242 4242" not in repr(card)

    def test_repr_never_exposes_the_cvc(self) -> None:
        card = _make_card("4242 4242 4242 4242", cvc="987")
        assert "987" not in repr(card)
        assert "cvc=***" in repr(card)

    def test_repr_keeps_non_sensitive_fields_readable(self) -> None:
        card = _make_card("4242 4242 4242 4242")
        assert "name='Jenny Rosen'" in repr(card)
        assert "expiration_date='12/34'" in repr(card)
