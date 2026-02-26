"""The Internet Basic Auth page object."""

import base64
import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from config.data.models import User
from pages.the_internet import locators as loc
from pages.the_internet.the_internet_base_page import TheInternetBasePage

logger = logging.getLogger(__name__)


class BasicAuthPage(TheInternetBasePage):
    """Represents the Basic Auth page on The Internet.

    Handles HTTP Basic Authentication via the ``Authorization`` header.
    Credentials must be set with :meth:`set_credentials` before navigating,
    otherwise the server returns ``401 Unauthorized``.

    Attributes:
        URL_PATH: Path to the Basic Auth page.
    """

    URL_PATH = "/basic_auth"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Locators ─────────────────────────────────────────────────────
        self._success_message: Locator = page.locator(loc.BASIC_AUTH_SUCCESS_MESSAGE)

    # ── Actions ──────────────────────────────────────────────────────────

    @allure.step("Set HTTP Basic Auth credentials for user '{user}'")
    def set_credentials(self, user: User) -> Self:
        """Set HTTP Basic Auth credentials via the Authorization header.

        Applies credentials to the browser context so all subsequent
        requests include the ``Authorization`` header.

        Args:
            user: Frozen dataclass with username and password.
        """
        logger.info("Setting HTTP Basic Auth credentials for user: %s", user)
        token = base64.b64encode(f"{user.username}:{user.password}".encode()).decode()
        self._page.context.set_extra_http_headers({"Authorization": f"Basic {token}"})
        return self

    @allure.step("Clear HTTP Basic Auth credentials")
    def clear_credentials(self) -> Self:
        """Remove HTTP Basic Auth credentials from the browser context."""
        logger.info("Clearing HTTP Basic Auth credentials")
        self._page.context.set_extra_http_headers({})
        return self

    # ── Getters ──────────────────────────────────────────────────────────

    @allure.step("Get success message text")
    def get_success_message(self) -> str:
        """Return the text of the success message after authentication."""
        logger.info("Getting success message text")
        return self._success_message.inner_text()

    @allure.step("Navigate to Basic Auth page and get HTTP status")
    def navigate_and_get_status(self) -> int:
        """Navigate to the Basic Auth page and return the HTTP response status.

        Returns:
            HTTP status code of the navigation response.
        """
        url = f"{self._base_url}{self.URL_PATH}"
        logger.info("Navigating to: %s", url)
        response = self._page.goto(url)
        status = response.status if response else 0
        logger.info("Response status: %s", status)
        return status

    # ── Verification ─────────────────────────────────────────────────────

    @allure.step("Verify successful authentication")
    def verify_successful_auth(self) -> Self:
        """Assert the page shows the authentication success message."""
        logger.info("Verifying successful authentication")
        expect(self._page_heading).to_have_text("Basic Auth")
        expect(self._success_message).to_contain_text("Congratulations")
        return self

    @allure.step("Verify Basic Auth page is loaded")
    def verify_page_loaded(self) -> Self:
        """Assert the page heading and success message are visible."""
        logger.info("Verifying Basic Auth page is loaded")
        expect(self._page_heading).to_have_text("Basic Auth")
        expect(self._success_message).to_be_visible()
        return self

    @allure.step("Verify success message mentions congratulations and credentials")
    def verify_success_message_content(self) -> Self:
        """Assert the success message contains expected text fragments."""
        logger.info("Verifying success message content")
        expect(self._success_message).to_contain_text("Congratulations")
        expect(self._success_message).to_contain_text("proper credentials")
        return self

    @allure.step("Navigate and verify response is 401 Unauthorized")
    def navigate_and_verify_unauthorized(self) -> Self:
        """Navigate to the Basic Auth page and assert an HTTP 401 response.

        Returns:
            Self for method chaining.
        """
        url = f"{self._base_url}{self.URL_PATH}"
        logger.info("Navigating to: %s", url)
        response = self._page.goto(url)
        status = response.status if response else 0
        logger.info("Response status: %s", status)
        assert status == 401, f"Expected 401 Unauthorized, got {status}"  # noqa: S101
        return self
