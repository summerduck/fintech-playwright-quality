"""Pytest fixtures for Accept a Payment tests.

Provides page object fixtures so tests receive ready-to-use page
instances without instantiating them directly. Each page fixture
resolves its own base URL from the page's ``APP_NAME`` and the
session-scoped ``env`` fixture.
"""

import pytest
from playwright.sync_api import Page

from config import get_base_url
from config.data.models import Card
from config.data.test_cards import TestCard
from pages.accept_a_payment.card_page import CardPage
from pages.accept_a_payment.three_ds_page import ThreeDSPage


@pytest.fixture
def card_page(page: Page, env: str) -> CardPage:
    """Provide a CardPage instance for the current test."""
    base_url = get_base_url(CardPage.APP_NAME, env)
    return CardPage(page, base_url)


@pytest.fixture
def three_ds_page(page: Page, env: str) -> ThreeDSPage:
    """Provide a ThreeDSPage instance for the current test."""
    base_url = get_base_url(ThreeDSPage.APP_NAME, env)
    return ThreeDSPage(page, base_url)


@pytest.fixture
def visa_card() -> Card:
    """Provide a Visa test card instance for the current test."""
    return TestCard.visa()
