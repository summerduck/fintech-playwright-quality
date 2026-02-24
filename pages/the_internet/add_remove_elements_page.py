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

    @allure.step("Click 'Add Element' button")
    def click_add_element(self) -> Self:
        """Click the Add Element button to create a new Delete button."""
        logger.info("Clicking 'Add Element' button")
        self._add_element_button.click()
        return self

    @allure.step("Click Delete button at index {index}")
    def click_delete_element(self, index: int = 0) -> Self:
        """Click a Delete button by its zero-based index.

        Args:
            index: Zero-based position of the Delete button to click.
        """
        logger.info("Clicking Delete button at index: %s", index)
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
