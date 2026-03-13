"""The Internet Context Menu page object."""

from __future__ import annotations

import logging
from typing import Self

import allure
from playwright.sync_api import Dialog, Locator, Page, expect

from pages.the_internet import locators as loc
from pages.the_internet.the_internet_base_page import TheInternetBasePage

logger = logging.getLogger(__name__)


class ContextMenuPage(TheInternetBasePage):
    """Represents the Context Menu page on The Internet.

    The page contains a single interactive element — a box with id ``#hot-spot``.
    Right-clicking it fires a JavaScript ``window.alert`` with the text
    "You selected a context menu". Left-clicking produces no alert.

    Attributes:
        URL_PATH: Path to the Context Menu page.
    """

    URL_PATH = "/context_menu"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Locators ─────────────────────────────────────────────────────
        self._hot_spot: Locator = page.locator(loc.CONTEXT_MENU_HOT_SPOT)

    # ── Getters ──────────────────────────────────────────────────────────

    @allure.step("Right-click hot-spot and return alert text")
    def right_click_hot_spot_and_get_alert_text(self) -> str:
        """Right-click the hot-spot, accept the JS alert, and return its message."""
        logger.info("Right-clicking hot-spot and capturing alert text")
        message_holder: list[str] = []

        def _handle_dialog(dialog: Dialog) -> None:
            message_holder.append(dialog.message)
            dialog.accept()

        self._page.once("dialog", _handle_dialog)
        self._hot_spot.click(button="right")
        if not message_holder:
            raise RuntimeError(
                "No dialog was captured after right-clicking the hot-spot"
            )
        return message_holder[0]

    @allure.step("Left-click hot-spot and check if an alert fired")
    def left_click_hot_spot_and_check_alert_fired(self) -> bool:
        """Left-click the hot-spot and return True if a JS dialog was triggered."""
        logger.info("Left-clicking hot-spot to check whether an alert fires")
        dialog_fired: list[bool] = []

        def _handle_dialog(dialog: Dialog) -> None:
            dialog_fired.append(True)
            dialog.accept()

        self._page.once("dialog", _handle_dialog)
        self._hot_spot.click()
        self._page.remove_listener("dialog", _handle_dialog)
        return bool(dialog_fired)

    # ── Verification ─────────────────────────────────────────────────────

    @allure.step("Verify Context Menu page is loaded")
    def verify_page_loaded(self) -> Self:
        """Assert the page heading is visible and reads 'Context Menu'."""
        logger.info("Verifying Context Menu page is loaded")
        expect(self._page_heading).to_be_visible()
        expect(self._page_heading).to_have_text("Context Menu")
        return self

    @allure.step("Verify current URL ends with /context_menu")
    def verify_url_is_context_menu(self) -> Self:
        """Assert the current page URL ends with '/context_menu'."""
        logger.info("Verifying URL ends with /context_menu")
        assert self._page.url.endswith("/context_menu"), (
            f"Expected URL to end with '/context_menu', got: {self._page.url}"
        )
        return self
