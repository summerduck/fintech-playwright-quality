import base64
import logging
from typing import Self

import allure
from playwright.sync_api import FrameLocator, Locator, Page, expect

from config.data.models import User
from pages.accept_a_payment import locators as loc
from pages.accept_a_payment.accept_a_payment_base_page import AcceptAPaymentBasePage

logger = logging.getLogger(__name__)


class ThreeDSPage(AcceptAPaymentBasePage):
    """Represents the Card page on Accept a Payment."""

    URL_PATH = "/card.html"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Locators ─────────────────────────────────────────────────────
        _wrapper: FrameLocator = page.frame_locator(loc.THREE_DS_WRAPPER_FRAME)
        self._three_ds_frame_element: Locator = _wrapper.locator(loc.THREE_DS_FRAME)
        self._three_ds_frame: FrameLocator = _wrapper.frame_locator(loc.THREE_DS_FRAME)
        self._three_ds_fail_button: Locator = self._three_ds_frame.locator(
            loc.THREE_DS_FAIL_BUTTON
        )
        self._three_ds_complete_button: Locator = self._three_ds_frame.locator(
            loc.THREE_DS_COMPLETE_BUTTON
        )

    # ── Navigation ───────────────────────────────────────────────────────
    @allure.step("Navigate to the three ds page")
    def navigate(self) -> Self:
        """Navigate to the three ds page."""
        raise NotImplementedError(
            "Cannot navigate to the three ds page directly. It is automatically navigated to after the card page is submitted."
        )

    # ── Actions ──────────────────────────────────────────────────────────

    @allure.step("Click the three ds fail button")
    def click_three_ds_fail_button(self) -> Self:
        """Click the three ds fail button."""
        logger.info("Clicking three ds fail button")
        expect(self._three_ds_fail_button).to_be_visible(timeout=30_000)
        expect(self._three_ds_fail_button).to_be_enabled(timeout=30_000)
        self._three_ds_fail_button.click()
        return self

    @allure.step("Click the three ds complete button")
    def click_three_ds_complete_button(self) -> Self:
        """Click the three ds complete button."""
        logger.info("Clicking three ds complete button")
        expect(self._three_ds_complete_button).to_be_visible(timeout=30_000)
        expect(self._three_ds_complete_button).to_be_enabled(timeout=30_000)
        self._three_ds_complete_button.click()
        return self

    # ── Wait for ──────────────────────────────────────────────────────────

    @allure.step("Wait for the three ds frame to be visible")
    def wait_for_three_ds_frame(self) -> Self:
        """Wait for the three ds frame to be visible."""
        logger.info("Waiting for three ds frame to be visible")
        expect(self._three_ds_frame_element).to_be_visible(timeout=30_000)
        self._page.wait_for_load_state("networkidle", timeout=30_000)
        return self

    @allure.step("Wait for the three ds frame to be hidden")
    def wait_for_three_ds_frame_to_be_hidden(self) -> Self:
        """Wait for the three ds frame to be hidden."""
        logger.info("Waiting for three ds frame to be hidden")
        expect(self._three_ds_frame_element).to_be_hidden(timeout=30_000)
        return self
