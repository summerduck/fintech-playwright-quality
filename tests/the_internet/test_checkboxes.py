"""Tests for Checkboxes on The Internet."""

import logging

import allure
import pytest

from pages.the_internet.checkboxes_page import CheckboxesPage

logger = logging.getLogger(__name__)


@allure.epic("The Internet")
@allure.feature("Checkboxes")
class TestCheckboxes:
    """Checkboxes test suite for The Internet."""

    @allure.story("Page Load")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checkboxes page loads with heading visible")
    @pytest.mark.theinternet
    @pytest.mark.smoke
    def test_page_loads_successfully(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify the Checkboxes page loads and displays the heading."""
        # Arrange
        checkboxes_page.navigate()

        # Act & Assert
        checkboxes_page.verify_page_loaded()

    @allure.story("Initial State")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checkbox 1 is unchecked on initial page load")
    @pytest.mark.theinternet
    @pytest.mark.smoke
    def test_checkbox_1_is_unchecked_on_load(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify checkbox 1 (index 0) is unchecked when the page first loads."""
        # Arrange
        checkboxes_page.navigate()

        # Act & Assert
        checkboxes_page.verify_checkbox_is_unchecked(0)

    @allure.story("Initial State")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checkbox 2 is checked on initial page load")
    @pytest.mark.theinternet
    @pytest.mark.smoke
    def test_checkbox_2_is_checked_on_load(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify checkbox 2 (index 1) is checked when the page first loads."""
        # Arrange
        checkboxes_page.navigate()

        # Act & Assert
        checkboxes_page.verify_checkbox_is_checked(1)

    @allure.story("Check Checkbox")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Checking Checkbox 1 marks it as checked")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_check_checkbox_1(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify checking checkbox 1 marks it as checked."""
        # Arrange
        checkboxes_page.navigate()

        # Act
        checkboxes_page.check_checkbox(0)

        # Assert
        checkboxes_page.verify_checkbox_is_checked(0)

    @allure.story("Uncheck Checkbox")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Unchecking Checkbox 2 marks it as unchecked")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_uncheck_checkbox_2(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify unchecking checkbox 2 marks it as unchecked."""
        # Arrange
        checkboxes_page.navigate()

        # Act
        checkboxes_page.uncheck_checkbox(1)

        # Assert
        checkboxes_page.verify_checkbox_is_unchecked(1)

    @allure.story("Toggle Checkbox")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Toggling Checkbox 1 twice returns it to unchecked")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_toggle_checkbox_1_back_to_unchecked(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify checkbox 1 can be toggled back to unchecked after being checked."""
        # Arrange
        checkboxes_page.navigate()
        checkboxes_page.check_checkbox(0)

        # Act
        checkboxes_page.uncheck_checkbox(0)

        # Assert
        checkboxes_page.verify_checkbox_is_unchecked(0)

    @allure.story("Toggle Checkbox")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Toggling Checkbox 2 twice returns it to checked")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_toggle_checkbox_2_back_to_checked(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify checkbox 2 can be toggled back to checked after being unchecked."""
        # Arrange
        checkboxes_page.navigate()
        checkboxes_page.uncheck_checkbox(1)

        # Act
        checkboxes_page.check_checkbox(1)

        # Assert
        checkboxes_page.verify_checkbox_is_checked(1)

    @allure.story("Combined State")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Both checkboxes can be checked simultaneously")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_both_checkboxes_checked_simultaneously(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify both checkboxes can be in the checked state at the same time."""
        # Arrange
        checkboxes_page.navigate()

        # Act
        checkboxes_page.check_checkbox(0)
        checkboxes_page.check_checkbox(1)

        # Assert
        checkboxes_page.verify_checkbox_is_checked(0)
        checkboxes_page.verify_checkbox_is_checked(1)

    @allure.story("Combined State")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Both checkboxes can be unchecked simultaneously")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_both_checkboxes_unchecked_simultaneously(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify both checkboxes can be in the unchecked state at the same time."""
        # Arrange
        checkboxes_page.navigate()

        # Act
        checkboxes_page.uncheck_checkbox(0)
        checkboxes_page.uncheck_checkbox(1)

        # Assert
        checkboxes_page.verify_checkbox_is_unchecked(0)
        checkboxes_page.verify_checkbox_is_unchecked(1)
