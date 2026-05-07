"""The Internet Basic Auth page object."""

import base64
import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from config.data.models import Card
from config.data.card_messages import CardMessages
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
        _stripe_frame = page.frame_locator(f"{loc.CARD_ELEMENT} iframe")
        self._card_input: Locator = _stripe_frame.locator(loc.CARD_INPUT)
        self._cvc_input: Locator = _stripe_frame.locator(loc.CVC_INPUT)
        self._expiration_date_input: Locator = _stripe_frame.locator(
            loc.EXPIRATION_DATE_INPUT
        )
        self._zip_input: Locator = _stripe_frame.locator(loc.ZIP_INPUT)

    # ── Actions ──────────────────────────────────────────────────────────

    @allure.step("Fill the card number input with the given card number")
    def fill_card_number(self, card_number: str) -> Self:
        """Fill the card number input with the given card number."""
        logger.info("Filling card number: %s", card_number)
        self._card_input.fill(card_number)
        return self

    @allure.step("Fill the name input with the given name")
    def fill_name(self, name: str) -> Self:
        """Fill the name input with the given name."""
        logger.info("Filling name: %s", name)
        self._name_input.fill(name)
        return self

    @allure.step("Fill the cvc input with the given cvc")
    def fill_cvc(self, cvc: str) -> Self:
        """Fill the cvc input with the given cvc."""
        logger.info("Filling cvc: %s", cvc)
        self._cvc_input.fill(cvc)
        return self

    @allure.step("Fill the expiration date input with the given expiration date")
    def fill_expiration_date(self, expiration_date: str) -> Self:
        """Fill the expiration date input with the given expiration date."""
        logger.info("Filling expiration date: %s", expiration_date)
        self._expiration_date_input.fill(expiration_date)
        return self

    @allure.step("Fill the ZIP/postal code input with the given ZIP/postal code")
    def fill_zip(self, zip_code: str) -> Self:
        """Fill the ZIP/postal code input."""
        logger.info("Filling ZIP: %s", zip_code)
        self._zip_input.fill(zip_code)
        return self

    @allure.step("Fill the card form with the given card")
    def fill_card_form(self, card: Card) -> Self:
        """Fill the card form with the given card."""
        self.fill_name(card.name)
        self.fill_card_number(card.number)
        self.fill_cvc(card.cvc)
        self.fill_expiration_date(card.expiration_date)
        self.fill_zip(card.zip_code)
        return self

    @allure.step("Click the pay button")
    def click_pay_button(self) -> Self:
        """Click the pay button."""
        logger.info("Clicking pay button")
        self._pay_button.click()
        return self

    # ── Getters ──────────────────────────────────────────────────────────

    @allure.step("Get the messages element")
    def get_messages(self) -> Locator:
        """Get the messages element."""
        logger.info("Getting messages element")
        expect(self._messages).to_be_visible(timeout=10_000)
        messages = self._messages.inner_text()
        logger.info(messages)
        return messages

    # ── Verification ─────────────────────────────────────────────────────

    @allure.step("Verify the card errors are visible")
    def verify_card_errors_are_visible(self) -> Self:
        """Verify the card errors are visible."""
        logger.info("Verifying card errors are visible")
        expect(self._card_errors).to_be_visible(timeout=30_000)
        return self

    @allure.step("Verify the card errors are not visible")
    def verify_card_errors_are_not_visible(self) -> Self:
        """Verify the card errors are not visible."""
        logger.info("Verifying card errors are not visible")
        expect(self._card_errors).to_be_hidden(timeout=30_000)
        return self

    @allure.step("Verify the pay button is enabled")
    def verify_pay_button_is_enabled(self) -> Self:
        """Verify the pay button is enabled."""
        logger.info("Verifying pay button is enabled")
        expect(self._pay_button).to_be_enabled(timeout=30_000)
        return self

    @allure.step("Verify the pay button is disabled")
    def verify_pay_button_is_disabled(self) -> Self:
        """Verify the pay button is disabled."""
        logger.info("Verifying pay button is disabled")
        expect(self._pay_button).to_be_disabled(timeout=30_000)
        return self

    @allure.step("Verify the messages contain the given text")
    def verify_messages_contain_text(self, messages: CardMessages) -> Self:
        """Verify the messages contain the given text."""
        logger.info("Verifying messages contain text: %s", messages)
        expect(self._messages).to_contain_text(messages)
        return self
