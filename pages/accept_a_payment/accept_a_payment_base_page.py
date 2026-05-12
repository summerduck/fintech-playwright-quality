"""Accept a Payment domain base page — shared components across Accept a Payment pages."""

import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from pages.accept_a_payment import locators as loc

logger = logging.getLogger(__name__)


class AcceptAPaymentBasePage(BasePage):
    """Shared base for all Accept a Payment page objects."""

    APP_NAME = "acceptapayment"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Shared locators ───────────────────────────────────────────
        self._page_heading: Locator = page.locator(loc.PAGE_HEADING)

    # ── Getters ──────────────────────────────────────────────────────────

    @allure.step("Get page heading text")
    def get_page_heading(self) -> str:
        """Return the text of the page heading."""
        logger.info("Getting page heading text")
        return self._page_heading.inner_text()

    # ── Actions ──────────────────────────────────────────────────────────

    # ── Verification ─────────────────────────────────────────────────────
