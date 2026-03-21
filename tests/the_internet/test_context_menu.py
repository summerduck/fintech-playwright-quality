"""Tests for Context Menu on The Internet."""

import allure
import pytest

from pages.the_internet.context_menu_page import ContextMenuPage


@allure.epic("The Internet")
@allure.feature("Context Menu")
class TestContextMenu:
    """Context Menu test suite for The Internet."""

    @allure.story("Page Load")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Context Menu page loads with correct heading")
    @pytest.mark.theinternet
    @pytest.mark.smoke
    def test_page_loads_successfully(
        self,
        context_menu_page: ContextMenuPage,
    ) -> None:
        """Verify the Context Menu page loads and heading is visible."""
        # Arrange

        # Act
        context_menu_page.navigate()

        # Assert
        context_menu_page.verify_page_loaded()

    @allure.story("Right-Click Alert")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Right-clicking hot-spot fires a JS alert")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_right_click_fires_alert(
        self,
        context_menu_page: ContextMenuPage,
    ) -> None:
        """Verify that right-clicking the hot-spot fires a JS alert."""
        # Arrange
        context_menu_page.navigate()

        # Act
        alert_text = context_menu_page.right_click_hot_spot_and_get_alert_text()

        # Assert
        assert alert_text is not None

    @allure.story("Right-Click Alert")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Alert text is exactly 'You selected a context menu'")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_alert_text_is_correct(
        self,
        context_menu_page: ContextMenuPage,
    ) -> None:
        """Verify the alert text matches the expected context menu message."""
        # Arrange
        context_menu_page.navigate()

        # Act
        alert_text = context_menu_page.right_click_hot_spot_and_get_alert_text()

        # Assert
        assert alert_text == "You selected a context menu"

    @allure.story("Alert Dismissal")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Alert is dismissed successfully via accept()")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_alert_is_dismissed_without_hang(
        self,
        context_menu_page: ContextMenuPage,
    ) -> None:
        """Verify alert is dismissed without hanging and returns expected text."""
        # Arrange
        context_menu_page.navigate()

        # Act
        alert_text = context_menu_page.right_click_hot_spot_and_get_alert_text()

        # Assert
        assert alert_text == "You selected a context menu"

    @allure.story("Post-Dismissal State")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Page remains on /context_menu after alert is dismissed")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_page_state_after_alert_dismissed(
        self,
        context_menu_page: ContextMenuPage,
    ) -> None:
        """Verify page remains fully loaded on /context_menu after alert dismissal."""
        # Arrange
        context_menu_page.navigate()

        # Act
        context_menu_page.right_click_hot_spot_and_get_alert_text()

        # Assert
        context_menu_page.verify_page_loaded()
        context_menu_page.verify_url_is_context_menu()

    @allure.story("Negative — Left Click")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Left-clicking hot-spot does not trigger an alert")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_left_click_does_not_fire_alert(
        self,
        context_menu_page: ContextMenuPage,
    ) -> None:
        """Verify that left-clicking the hot-spot does not fire a JS alert."""
        # Arrange
        context_menu_page.navigate()

        # Act
        alert_fired = context_menu_page.left_click_hot_spot_and_check_alert_fired()

        # Assert
        assert alert_fired is False

    @pytest.mark.skip(
        reason="Cross-browser keyboard context-menu event instability (TC-07)"
    )
    @allure.story("Keyboard Context Menu")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Keyboard context menu (Shift+F10) on hot-spot fires an alert")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_keyboard_context_menu_fires_alert(
        self,
        context_menu_page: ContextMenuPage,
    ) -> None:
        """Keyboard context menu test — skipped due to cross-browser instability."""
        pass
