"""The Internet Basic Auth page object."""

import base64
import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from config.data.models import User
from pages.accept_a_payment import locators as loc
from pages.accept_a_payment.accept_a_payment_base_page import AcceptAPaymentBasePage

logger = logging.getLogger(__name__)


class CardPage(AcceptAPaymentBasePage):
    """Represents the Card page on Accept a Payment."""

    URL_PATH = "/card.html"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Locators ─────────────────────────────────────────────────────
        self._card_form: Locator = page.locator(loc.CARD_FORM)
        self._name_input: Locator = page.locator(loc.NAME_INPUT)
        self._card_element: Locator = page.locator(loc.CARD_ELEMENT)
        self._card_errors: Locator = page.locator(loc.CARD_ERRORS)
        self._pay_button: Locator = page.locator(loc.PAY_BUTTON)
        self._messages: Locator = page.locator(loc.MESSAGES)
        self._card_input: Locator = page.locator(loc.CARD_INPUT)

    # ── Actions ──────────────────────────────────────────────────────────

    def fill_card_number(self, card_number: str) -> Self:
        """Fill the card number input with the given card number."""
        logger.info("Filling card number: %s", card_number)
        self._card_input.fill(card_number)
        return self

    def fill_name(self, name: str) -> Self:
        """Fill the name input with the given name."""
        logger.info("Filling name: %s", name)
        self._name_input.fill(name)
        return self

    # ── Getters ──────────────────────────────────────────────────────────

    # ── Verification ─────────────────────────────────────────────────────
