"""Base page object — shared helpers for all page objects."""

import logging
from typing import Self

import allure
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class BasePage:
    """Universal base class for all page objects across all apps.

    Attributes:
        URL_PATH: Override in subclasses with the page's relative path.
    """

    URL_PATH = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        self._page = page
        self._base_url = base_url

    def navigate(self) -> Self:
        """Open the page by navigating to base_url + URL_PATH."""
        url = f"{self._base_url}{self.URL_PATH}"
        with allure.step(f"Navigate to {self.URL_PATH}"):
            logger.info("Navigating to: %s", url)
            self._page.goto(url)
        return self

    @allure.step("Take screenshot '{name}'")
    def take_screenshot(self, name: str = "screenshot") -> bytes:
        """Capture a screenshot and attach it to the Allure report."""
        screenshot = self._page.screenshot()
        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
        return screenshot
