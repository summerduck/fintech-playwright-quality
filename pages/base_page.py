"""Base page object — shared helpers for all page objects."""

import logging
from typing import Self

import allure
from pages.exceptions import NavigationError
from playwright.sync_api import Page, Response, expect

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

        self.response: Response | None = None

    def navigate(self) -> Response | None:
        """Open the page by navigating to base_url + URL_PATH."""
        url = f"{self._base_url}{self.URL_PATH}"
        with allure.step(f"Navigate to {self.URL_PATH}"):
            logger.info("Navigating to: %s", url)
            self.response = self._page.goto(url)

        return self.response

    @allure.step("Take screenshot '{name}'")
    def take_screenshot(self, name: str = "screenshot") -> bytes:
        """Capture a screenshot and attach it to the Allure report."""
        screenshot = self._page.screenshot()
        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
        return screenshot

    def verify_response_status(
        self,
    ) -> Self:
        """Verify the HTTP response status is 200. Raises NavigationError if the response is None or non-200."""
        match self.response:
            case None:
                message = f"No response from {self.URL_PATH}"
                logger.error(message)
                raise NavigationError(message)
            case resp if self.response.status != 200:
                message = f"{self.response.status} response from {self.URL_PATH}"
                logger.error(message)
                raise NavigationError(message)

        logger.info("%s response from %s", self.response.status, self.URL_PATH)
        return self
