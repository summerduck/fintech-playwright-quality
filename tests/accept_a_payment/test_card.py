"""Tests for the Accept a Payment card flow."""

import logging

import allure
import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from pages.accept_a_payment.card_page import CardPage

logger = logging.getLogger(__name__)


@allure.epic("Accept a Payment")
@allure.feature("Card")
class TestCard:
    """Card test suite for Accept a Payment."""

    @allure.story("Actions")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Fill the name input with the given name")
    @pytest.mark.acceptapayment
    @pytest.mark.smoke
    def test_fill_name(
        self,
        card_page: CardPage,
        name: str = "John Doe",
    ) -> None:
        """Fill the name input with the given name."""
        # Arrange
        card_page.navigate()

        # Act & Assert
        card_page.fill_name(name)
