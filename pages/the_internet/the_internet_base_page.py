"""The Internet domain base page — shared components across The Internet pages."""

import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage
from pages.the_internet import locators as loc

logger = logging.getLogger(__name__)


class TheInternetBasePage(BasePage):
    """Shared base for all The Internet page objects.

    Encapsulates the page heading, GitHub fork banner, and footer
    that appear across all The Internet pages.
    """

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Shared locators ───────────────────────────────────────────
        self._page_heading: Locator = page.locator(loc.PAGE_HEADING)
        self._github_fork_link: Locator = page.locator(loc.GITHUB_FORK_LINK)
        self._github_fork_image: Locator = page.locator(loc.GITHUB_FORK_IMAGE)
        self._page_footer: Locator = page.locator(loc.PAGE_FOOTER)
        self._footer_link: Locator = page.locator(loc.FOOTER_LINK)

    # ── Getters ──────────────────────────────────────────────────────────

    @allure.step("Get page heading text")
    def get_page_heading(self) -> str:
        """Return the text of the page heading."""
        logger.info("Getting page heading text")
        return self._page_heading.inner_text()

    @allure.step("Get footer text")
    def get_footer_text(self) -> str:
        """Return the text content of the page footer."""
        logger.info("Getting footer text")
        return self._page_footer.inner_text()

    # ── Actions ──────────────────────────────────────────────────────────

    @allure.step("Click 'Fork me on GitHub' link")
    def click_github_fork_link(self) -> Self:
        """Click the GitHub fork banner link."""
        logger.info("Clicking GitHub fork link")
        self._github_fork_link.click()
        return self

    # ── Verification ─────────────────────────────────────────────────────

    @allure.step("Verify GitHub fork banner is visible")
    def verify_github_fork_visible(self) -> Self:
        """Assert the 'Fork me on GitHub' image is visible."""
        logger.info("Verifying GitHub fork banner visibility")
        expect(self._github_fork_image).to_be_visible()
        return self

    @allure.step("Verify footer is visible")
    def verify_footer_visible(self) -> Self:
        """Assert the footer with 'Powered by Elemental Selenium' is visible."""
        logger.info("Verifying footer visibility")
        expect(self._page_footer).to_be_visible()
        expect(self._footer_link).to_have_text("Elemental Selenium")
        return self
