"""The Internet Broken Images page object."""

from __future__ import annotations

import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from pages.the_internet import locators as loc
from pages.the_internet.the_internet_base_page import TheInternetBasePage

logger = logging.getLogger(__name__)


class BrokenImagesPage(TheInternetBasePage):
    """Represents the Broken Images page on The Internet.

    The page displays three content images inside ``div.example``, two of which
    have broken sources. Image load state is detected via JavaScript evaluation
    of ``naturalWidth`` and ``complete`` after network idle.

    Attributes:
        URL_PATH: Path to the Broken Images page.
    """

    URL_PATH = "/broken_images"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Locators ─────────────────────────────────────────────────────
        self._content_images: Locator = self._page.locator(
            loc.BROKEN_IMAGES_CONTENT_IMAGES
        )

    # ── Navigation ───────────────────────────────────────────────────────

    @allure.step("Navigate to Broken Images page and wait for network idle")
    def navigate(self) -> Self:
        """Navigate to the Broken Images page and wait for network idle.

        Overrides ``BasePage.navigate()`` to call
        ``wait_for_load_state("networkidle")`` after navigation so that
        ``naturalWidth`` DOM properties are reliable before any assertions.
        """
        logger.info("Navigating to Broken Images page and waiting for network idle")
        super().navigate()
        self._page.wait_for_load_state("networkidle")
        return self

    # ── Getters ──────────────────────────────────────────────────────────

    @allure.step("Get total content image count")
    def get_total_image_count(self) -> int:
        """Return the total number of content images in div.example."""
        logger.info("Getting total content image count")
        return self._content_images.count()

    @allure.step("Get broken image count")
    def get_broken_image_count(self) -> int:
        """Return the number of broken images detected via naturalWidth === 0."""
        logger.info("Getting broken image count via JS evaluation")
        return int(
            self._page.evaluate(
                "() => { const imgs = document.querySelectorAll('div.example img');"
                " return Array.from(imgs)"
                ".filter(img => !img.complete || img.naturalWidth === 0).length; }"
            )
        )

    @allure.step("Get valid image count")
    def get_valid_image_count(self) -> int:
        """Return the number of valid images detected via naturalWidth > 0."""
        logger.info("Getting valid image count via JS evaluation")
        return int(
            self._page.evaluate(
                "() => { const imgs = document.querySelectorAll('div.example img');"
                " return Array.from(imgs)"
                ".filter(img => img.complete && img.naturalWidth > 0).length; }"
            )
        )

    @allure.step("Check all images have complete === true")
    def get_all_images_complete(self) -> bool:
        """Return True if every content image has complete === true."""
        logger.info("Checking all images have complete === true via JS evaluation")
        return bool(
            self._page.evaluate(
                "() => { const imgs = document.querySelectorAll('div.example img');"
                " return Array.from(imgs).every(img => img.complete); }"
            )
        )

    # ── Verification ─────────────────────────────────────────────────────

    @allure.step("Verify Broken Images page is loaded")
    def verify_page_loaded(self) -> Self:
        """Assert the page heading is visible and reads 'Broken Images'."""
        logger.info("Verifying Broken Images page is loaded")
        expect(self._page_heading).to_be_visible()
        expect(self._page_heading).to_have_text("Broken Images")
        return self

    @allure.step("Verify total content image count is {expected}")
    def verify_total_image_count(self, expected: int) -> Self:
        """Assert the total number of content images matches the expected count.

        Args:
            expected: Expected number of content images.
        """
        logger.info("Verifying total content image count is %s", expected)
        expect(self._content_images).to_have_count(expected)
        return self

    @allure.step("Verify broken image count is {expected}")
    def verify_broken_image_count(self, expected: int) -> Self:
        """Assert the number of broken images matches the expected count.

        Args:
            expected: Expected number of broken images.
        """
        logger.info("Verifying broken image count is %s", expected)
        actual = self.get_broken_image_count()
        assert actual == expected, (
            f"Expected {expected} broken image(s), found {actual}"
        )
        return self

    @allure.step("Verify valid image count is {expected}")
    def verify_valid_image_count(self, expected: int) -> Self:
        """Assert the number of valid images matches the expected count.

        Args:
            expected: Expected number of valid images.
        """
        logger.info("Verifying valid image count is %s", expected)
        actual = self.get_valid_image_count()
        assert actual == expected, f"Expected {expected} valid image(s), found {actual}"
        return self

    @allure.step("Verify broken + valid image counts sum to total")
    def verify_broken_plus_valid_equals_total(self) -> Self:
        """Assert that broken image count plus valid image count equals total."""
        logger.info("Verifying broken + valid image counts sum to total")
        broken = self.get_broken_image_count()
        valid = self.get_valid_image_count()
        total = self.get_total_image_count()
        assert broken + valid == total, (
            f"Expected broken ({broken}) + valid ({valid}) == total ({total})"
        )
        return self

    @allure.step("Verify all images have loaded (complete === true)")
    def verify_all_images_complete(self) -> Self:
        """Assert all content images have complete === true."""
        logger.info("Verifying all images have complete === true")
        result = self.get_all_images_complete()
        assert result is True, "Expected all images to have complete === true"
        return self

    @allure.step("Verify GitHub fork banner is not included in content images")
    def verify_fork_banner_not_in_content_images(self) -> Self:
        """Assert content image count is exactly 3, excluding the fork banner."""
        logger.info("Verifying GitHub fork banner is not included in content images")
        expect(self._content_images).to_have_count(3)
        assert self._content_images.count() < 4, (
            "Content image selector returned 4 or more — fork banner may be included"
        )
        return self
