"""The Internet Checkboxes page object."""

from __future__ import annotations

import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from pages.the_internet import locators as loc
from pages.the_internet.the_internet_base_page import TheInternetBasePage

logger = logging.getLogger(__name__)


class CheckboxesPage(TheInternetBasePage):
    """Represents the Checkboxes page on The Internet.

    The page contains two checkboxes where the first is unchecked and the
    second is checked by default.

    Attributes:
        URL_PATH: Path to the Checkboxes page.
    """

    URL_PATH = "/checkboxes"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Locators ─────────────────────────────────────────────────────
        self._checkboxes: Locator = self._page.locator(loc.CHECKBOXES_CHECKBOX)

    # ── Verification ─────────────────────────────────────────────────────

    @allure.step("Verify Checkboxes page is loaded")
    def verify_page_loaded(self) -> Self:
        """Assert the page heading is visible and reads 'Checkboxes'."""
        logger.info("Verifying Checkboxes page is loaded")
        expect(self._page_heading).to_be_visible()
        expect(self._page_heading).to_have_text("Checkboxes")
        return self

    @allure.step("Verify initial checkbox state")
    def verify_initial_state(self) -> Self:
        """Assert checkbox at index 0 is unchecked and index 1 is checked."""
        logger.info("Verifying initial checkbox state")
        self.verify_checkbox_is_unchecked(0)
        self.verify_checkbox_is_checked(1)
        return self

    @allure.step("Verify checkbox at index {index} is checked")
    def verify_checkbox_is_checked(self, index: int) -> Self:
        """Assert the checkbox at index is checked.

        Args:
            index: Zero-based index of the checkbox to verify.
        """
        logger.info("Verifying checkbox at index %s is checked", index)
        expect(self._checkboxes.nth(index)).to_be_checked()
        return self

    @allure.step("Verify checkbox at index {index} is unchecked")
    def verify_checkbox_is_unchecked(self, index: int) -> Self:
        """Assert the checkbox at index is unchecked.

        Args:
            index: Zero-based index of the checkbox to verify.
        """
        logger.info("Verifying checkbox at index %s is unchecked", index)
        expect(self._checkboxes.nth(index)).not_to_be_checked()
        return self

    # ── Getters ──────────────────────────────────────────────────────────

    @allure.step("Get checked state of checkbox at index {index}")
    def is_checkbox_checked(self, index: int) -> bool:
        """Return True if the checkbox at index is currently checked.

        Args:
            index: Zero-based index of the checkbox to inspect.
        """
        logger.info("Getting checked state of checkbox at index %s", index)
        return self._checkboxes.nth(index).is_checked()

    # ── Actions ──────────────────────────────────────────────────────────

    @allure.step("Check checkbox at index {index}")
    def check_checkbox(self, index: int) -> Self:
        """Check the checkbox at index.

        Args:
            index: Zero-based index of the checkbox to check.
        """
        logger.info("Checking checkbox at index %s", index)
        self._checkboxes.nth(index).check()
        return self

    @allure.step("Uncheck checkbox at index {index}")
    def uncheck_checkbox(self, index: int) -> Self:
        """Uncheck the checkbox at index.

        Args:
            index: Zero-based index of the checkbox to uncheck.
        """
        logger.info("Unchecking checkbox at index %s", index)
        self._checkboxes.nth(index).uncheck()
        return self
