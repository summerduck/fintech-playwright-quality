"""The Internet Add/Remove Elements page object."""

import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from pages.the_internet import locators as loc
from pages.the_internet.the_internet_base_page import TheInternetBasePage

logger = logging.getLogger(__name__)


class AddRemoveElementsPage(TheInternetBasePage):
    """Represents the Add/Remove Elements page on The Internet.

    Attributes:
        URL_PATH: Path to the Add/Remove Elements page.
    """

    URL_PATH = "/add_remove_elements/"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Locators ─────────────────────────────────────────────────────
        self._add_element_button: Locator = page.locator(loc.ADD_ELEMENT_BUTTON)
        self._delete_buttons: Locator = page.locator(loc.DELETE_BUTTON)

    # ── Actions ──────────────────────────────────────────────────────────

    @allure.step("Click 'Add Element' button {count} time(s)")
    def click_add_element(self, count: int = 1) -> Self:
        """Click the Add Element button one or more times.

        Args:
            count: Number of times to click the button.
        """
        logger.info("Clicking 'Add Element' button %s time(s)", count)
        for _ in range(count):
            self._add_element_button.click()
        return self

    @allure.step("Click Delete button at index {index}, {count} time(s)")
    def click_delete_element(self, index: int = 0, count: int = 1) -> Self:
        """Click Delete button(s) starting from a zero-based index.

        Removes *count* buttons, always clicking at *index* (since
        the list shifts after each removal).

        Args:
            index: Zero-based position of the Delete button to click.
            count: Number of Delete buttons to remove.
        """
        logger.info("Clicking Delete button at index %s, %s time(s)", index, count)
        for _ in range(count):
            self._delete_buttons.nth(index).click()
        return self

    # ── Getters ──────────────────────────────────────────────────────────

    @allure.step("Get Delete button count")
    def get_delete_button_count(self) -> int:
        """Return the number of Delete buttons currently visible."""
        count = self._delete_buttons.count()
        logger.info("Delete button count: %s", count)
        return count

    # ── Verification ─────────────────────────────────────────────────────

    @allure.step("Verify Add/Remove Elements page is loaded")
    def verify_page_loaded(self) -> Self:
        """Assert the page heading and Add Element button are visible."""
        logger.info("Verifying Add/Remove Elements page is loaded")
        expect(self._page_heading).to_have_text("Add/Remove Elements")
        expect(self._add_element_button).to_be_visible()
        return self

    @allure.step("Verify Delete button count is {expected_count}")
    def verify_delete_button_count(self, expected_count: int) -> Self:
        """Assert the exact number of Delete buttons visible.

        Args:
            expected_count: Expected number of Delete buttons.
        """
        logger.info("Verifying Delete button count is %s", expected_count)
        expect(self._delete_buttons).to_have_count(expected_count)
        return self
