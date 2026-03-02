"""The Internet Drag and Drop page object."""

import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from pages.the_internet import locators as loc
from pages.the_internet.the_internet_base_page import TheInternetBasePage

logger = logging.getLogger(__name__)


class DragAndDropPage(TheInternetBasePage):
    """Represents the Drag and Drop page on The Internet.

    The page contains two columns (A and B). Dragging one column onto
    the other swaps their DOM order. Positional verification uses
    ``:first-child`` / ``:last-child`` selectors against the live DOM.

    Attributes:
        URL_PATH: Path to the Drag and Drop page.
    """

    URL_PATH = "/drag_and_drop"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Locators ─────────────────────────────────────────────────────
        self._column_a: Locator = page.locator(loc.DRAG_DROP_COLUMN_A)
        self._column_b: Locator = page.locator(loc.DRAG_DROP_COLUMN_B)
        self._column_a_header: Locator = page.locator(loc.DRAG_DROP_COLUMN_A_HEADER)
        self._column_b_header: Locator = page.locator(loc.DRAG_DROP_COLUMN_B_HEADER)
        self._first_column_header: Locator = page.locator(
            loc.DRAG_DROP_FIRST_COLUMN_HEADER
        )
        self._second_column_header: Locator = page.locator(
            loc.DRAG_DROP_SECOND_COLUMN_HEADER
        )

    # ── Actions ──────────────────────────────────────────────────────────

    @allure.step("Drag column A onto column B {count} time(s)")
    def drag_column_a_to_b(self, count: int = 1) -> Self:
        """Drag column A onto column B one or more times.

        Args:
            count: Number of times to perform the drag.
        """
        logger.info("Dragging column A onto column B %s time(s)", count)
        for _ in range(count):
            self._column_a.drag_to(self._column_b)
        return self

    @allure.step("Drag column B onto column A {count} time(s)")
    def drag_column_b_to_a(self, count: int = 1) -> Self:
        """Drag column B onto column A one or more times.

        Args:
            count: Number of times to perform the drag.
        """
        logger.info("Dragging column B onto column A %s time(s)", count)
        for _ in range(count):
            self._column_b.drag_to(self._column_a)
        return self

    # ── Getters ──────────────────────────────────────────────────────────

    @allure.step("Get column A label text")
    def get_column_a_label(self) -> str:
        """Return the text of the header inside #column-a."""
        label = self._column_a_header.inner_text()
        logger.info("Column A label: %s", label)
        return label

    @allure.step("Get column B label text")
    def get_column_b_label(self) -> str:
        """Return the text of the header inside #column-b."""
        label = self._column_b_header.inner_text()
        logger.info("Column B label: %s", label)
        return label

    @allure.step("Get first column label (DOM order)")
    def get_first_column_label(self) -> str:
        """Return the label of the first column by current DOM position."""
        label = self._first_column_header.inner_text()
        logger.info("First column label (DOM): %s", label)
        return label

    @allure.step("Get second column label (DOM order)")
    def get_second_column_label(self) -> str:
        """Return the label of the second column by current DOM position."""
        label = self._second_column_header.inner_text()
        logger.info("Second column label (DOM): %s", label)
        return label

    # ── Verification ─────────────────────────────────────────────────────

    @allure.step("Verify Drag and Drop page is loaded")
    def verify_page_loaded(self) -> Self:
        """Assert the page heading and both columns are visible."""
        logger.info("Verifying Drag and Drop page is loaded")
        expect(self._page_heading).to_have_text("Drag and Drop")
        expect(self._column_a).to_be_visible()
        expect(self._column_b).to_be_visible()
        return self

    @allure.step("Verify columns are in default order (A first, B second)")
    def verify_columns_in_default_order(self) -> Self:
        """Assert column A is the first child and column B is the second child."""
        logger.info("Verifying default order: A first, B second")
        expect(self._first_column_header).to_have_text("A")
        expect(self._second_column_header).to_have_text("B")
        return self

    @allure.step("Verify columns are swapped (B first, A second)")
    def verify_columns_swapped(self) -> Self:
        """Assert column B is the first child and column A is the second child."""
        logger.info("Verifying swapped order: B first, A second")
        expect(self._first_column_header).to_have_text("B")
        expect(self._second_column_header).to_have_text("A")
        return self
