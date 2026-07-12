"""3D Secure challenge frame — a component rendered on top of the card page.

This is not a page. The 3DS challenge is a nested iframe that Stripe mounts on
card.html after the pay button is clicked; it cannot be navigated to directly.
It is therefore owned by ``CardPage`` instead of inheriting from a page base
class that would promise a ``navigate()`` it cannot honour.
"""

import logging
from typing import Self

import allure
from playwright.sync_api import FrameLocator, Locator, Page, expect

from pages.accept_a_payment import locators as loc
from pages.accept_a_payment.constants import PAYMENT_TIMEOUT

logger = logging.getLogger(__name__)


class ThreeDSFrame:
    """Represents the 3D Secure authentication overlay on the card page."""

    def __init__(self, page: Page) -> None:
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

    # ── Actions ──────────────────────────────────────────────────────────

    @allure.step("Click the three ds fail button")
    def click_three_ds_fail_button(self) -> Self:
        """Click the three ds fail button."""
        logger.info("Clicking three ds fail button")
        expect(self._three_ds_fail_button).to_be_visible(timeout=PAYMENT_TIMEOUT)
        expect(self._three_ds_fail_button).to_be_enabled(timeout=PAYMENT_TIMEOUT)
        self._three_ds_fail_button.click()
        return self

    @allure.step("Click the three ds complete button")
    def click_three_ds_complete_button(self) -> Self:
        """Click the three ds complete button."""
        logger.info("Clicking three ds complete button")
        expect(self._three_ds_complete_button).to_be_visible(timeout=PAYMENT_TIMEOUT)
        expect(self._three_ds_complete_button).to_be_enabled(timeout=PAYMENT_TIMEOUT)
        self._three_ds_complete_button.click()
        return self

    @allure.step("Handle the three ds challenge")
    def handle_three_ds(
        self,
        requires_3ds: bool = True,
        fail: bool = False,
    ) -> Self:
        """Complete or fail the 3DS challenge, or do nothing if not required."""
        if not requires_3ds:
            logger.info("Three ds is not required")
            return self

        self.wait_for_three_ds_frame()
        if fail:
            self.click_three_ds_fail_button()
        else:
            self.click_three_ds_complete_button()
        self.wait_for_three_ds_frame_to_be_hidden()
        return self

    # ── Wait for ──────────────────────────────────────────────────────────

    @allure.step("Wait for the three ds frame to be visible")
    def wait_for_three_ds_frame(self) -> Self:
        """Wait for the three ds frame to be visible."""
        logger.info("Waiting for three ds frame to be visible")
        expect(self._three_ds_frame_element).to_be_visible(timeout=PAYMENT_TIMEOUT)
        return self

    @allure.step("Wait for the three ds frame to be hidden")
    def wait_for_three_ds_frame_to_be_hidden(self) -> Self:
        """Wait for the three ds frame to be hidden."""
        logger.info("Waiting for three ds frame to be hidden")
        expect(self._three_ds_frame_element).to_be_hidden(timeout=PAYMENT_TIMEOUT)
        return self
