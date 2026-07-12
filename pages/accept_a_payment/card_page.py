"""Card payment page object for the Accept a Payment demo app."""

import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from config.data.card_messages import CardMessages
from config.data.models import Card
from pages.accept_a_payment import locators as loc
from pages.accept_a_payment.accept_a_payment_base_page import AcceptAPaymentBasePage
from pages.accept_a_payment.constants import PAYMENT_TIMEOUT

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
        self._dashboard_link: Locator = page.locator(loc.DASHBOARD_LINK)

    # ── Actions ──────────────────────────────────────────────────────────

    @allure.step("Fill the card number input with the given card number")
    def fill_card_number(self, card_number: str) -> Self:
        """Fill the card number input with the given card number."""
        logger.info("Filling card number")
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
        logger.info("Filling cvc")
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
        logger.info("Filling card form with card: %s", card)
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
    def get_messages(self) -> str:
        """Get the messages element."""
        logger.info("Getting messages element")
        self._wait_for_messages_to_be_visible()
        messages = self._messages.inner_text()
        logger.info(messages)
        return messages

    @allure.step("Get the dashboard link URL")
    def get_dashboard_link(self) -> str | None:
        """Get the dashboard link URL from the href attribute."""
        logger.info("Getting dashboard link element")
        return self._dashboard_link.get_attribute("href")

    @allure.step("Get the payment intent ID from the dashboard link")
    def get_payment_id(self) -> str | None:
        """Get the payment ID from the dashboard link element."""
        logger.info("Getting payment ID from dashboard link element")
        return self._dashboard_link.text_content()

    # ── Verification ─────────────────────────────────────────────────────

    @allure.step("Verify the dashboard link is visible")
    def verify_dashboard_link_is_visible(self) -> Self:
        """Verify the dashboard link is visible."""
        logger.info("Verifying dashboard link is visible")
        self._wait_for_messages_to_be_visible()
        expect(self._dashboard_link).to_be_visible()
        expect(self._dashboard_link).to_have_attribute("target", "_blank")
        return self

    @allure.step("Verify the card errors are visible")
    def verify_card_errors_are_visible(self) -> Self:
        """Verify the card errors are visible."""
        logger.info("Verifying card errors are visible")
        expect(self._card_errors).to_be_visible(timeout=PAYMENT_TIMEOUT)
        return self

    @allure.step("Verify the card errors are not visible")
    def verify_card_errors_are_not_visible(self) -> Self:
        """Verify the card errors are not visible."""
        logger.info("Verifying card errors are not visible")
        expect(self._card_errors).to_be_hidden(timeout=PAYMENT_TIMEOUT)
        return self

    @allure.step("Verify the pay button is enabled")
    def verify_pay_button_is_enabled(self) -> Self:
        """Verify the pay button is enabled."""
        logger.info("Verifying pay button is enabled")
        expect(self._pay_button).to_be_enabled(timeout=PAYMENT_TIMEOUT)
        return self

    @allure.step("Verify the pay button is disabled")
    def verify_pay_button_is_disabled(self) -> Self:
        """Verify the pay button is disabled."""
        logger.info("Verifying pay button is disabled")
        expect(self._pay_button).to_be_disabled(timeout=PAYMENT_TIMEOUT)
        return self

    @allure.step("Verify the messages contain the given text")
    def verify_messages_contain_text(self, messages: CardMessages) -> Self:
        """Verify the messages contain the given text."""
        logger.info("Verifying messages contain text: %s", messages)
        expect(self._messages).to_contain_text(messages)
        return self

    # ── Wait for ─────────────────────────────────────────────────────

    def _wait_for_messages_to_be_visible(self) -> Self:
        """Wait for the messages element to be visible."""
        logger.debug("Waiting for messages to be visible")
        expect(self._messages).to_be_visible(timeout=10_000)
        return self

    @allure.step("Assert page title is 'Card'")
    def verify_page_title_is_card(self) -> Self:
        """Assert that the page title is 'Card'."""
        logger.info("Verifying page title equals 'Card'")
        expect(self._page).to_have_title("Card")
        return self

    @allure.step("Verify Stripe card element iframe is visible in #card-element")
    def verify_stripe_card_element_iframe_visible(self) -> Self:
        """Assert Stripe iframe is mounted and visible within #card-element."""
        logger.info("Verifying Stripe card element iframe is visible in #card-element")
        expect(self._card_element).to_be_visible()
        return self

    @allure.step("Verify #messages panel is hidden on load")
    def verify_messages_panel_is_hidden(self) -> Self:
        """Assert #messages panel is hidden on page load."""
        logger.info("Verifying #messages panel is hidden on load")
        expect(self._messages).to_be_hidden()
        return self

    @allure.step("Verify #card-errors is empty on load")
    def verify_card_errors_are_empty_on_load(self) -> Self:
        """Assert #card-errors element is empty at page load."""
        logger.info("Verifying #card-errors is empty on load")
        expect(self._card_errors).to_have_text("")
        return self

    @allure.step("Verify pay button is enabled on load")
    def verify_pay_button_is_enabled_on_load(self) -> Self:
        """Assert the pay button is enabled at page load."""
        logger.info("Verifying pay button is enabled on load")
        expect(self._pay_button).to_be_enabled()
        return self

    @allure.step("Verify name input is pre-filled with 'Jenny Rosen'")
    def verify_name_input_prefilled_jenny_rosen(self) -> Self:
        """Assert #name input is pre-filled with 'Jenny Rosen'."""
        logger.info("Verifying #name input is pre-filled with 'Jenny Rosen'")
        expect(self._name_input).to_have_value("Jenny Rosen")
        return self
