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
    @allure.title("Both checkboxes are in their correct initial state on page load")
    @pytest.mark.theinternet
    @pytest.mark.smoke
    def test_both_checkboxes_initial_state(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify both checkboxes are in their expected initial state after page load."""
        # Arrange
        checkboxes_page.navigate()

        # Act & Assert
        checkboxes_page.verify_initial_state()

    @allure.story("Checkbox Independence")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checking Checkbox 1 leaves Checkbox 2 unaffected")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_checking_checkbox_1_does_not_affect_checkbox_2(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify checking checkbox 1 does not change the state of checkbox 2."""
        # Arrange
        checkboxes_page.navigate()

        # Act
        checkboxes_page.check_checkbox(0)

        # Assert
        checkboxes_page.verify_checkbox_is_checked(0)
        checkboxes_page.verify_checkbox_is_checked(1)

    @allure.story("Checkbox Independence")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Unchecking Checkbox 2 leaves Checkbox 1 unaffected")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_unchecking_checkbox_2_does_not_affect_checkbox_1(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify unchecking checkbox 2 does not change the state of checkbox 1."""
        # Arrange
        checkboxes_page.navigate()

        # Act
        checkboxes_page.uncheck_checkbox(1)

        # Assert
        checkboxes_page.verify_checkbox_is_unchecked(1)
        checkboxes_page.verify_checkbox_is_unchecked(0)

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
        checkboxes_page.uncheck_checkbox(1)

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
        checkboxes_page.check_checkbox(0)

        # Act
        checkboxes_page.uncheck_checkbox(0)
        checkboxes_page.uncheck_checkbox(1)

        # Assert
        checkboxes_page.verify_checkbox_is_unchecked(0)
        checkboxes_page.verify_checkbox_is_unchecked(1)

    @allure.story("Label Text")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checkbox label text matches expected value")
    @pytest.mark.theinternet
    @pytest.mark.regression
    @pytest.mark.parametrize("index, expected", [(0, "checkbox 1"), (1, "checkbox 2")])
    def test_checkbox_labels_text(
        self,
        checkboxes_page: CheckboxesPage,
        index: int,
        expected: str,
    ) -> None:
        """Verify each checkbox label displays the expected text."""
        # Arrange
        checkboxes_page.navigate()

        # Act & Assert
        checkboxes_page.verify_label_text(index, expected)

    @allure.story("Double Click")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Double-clicking an unchecked checkbox leaves it unchecked")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_double_click_leaves_unchecked_checkbox_unchanged(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify double-clicking an unchecked checkbox leaves it unchecked."""
        # Arrange
        checkboxes_page.navigate()

        # Act
        checkboxes_page.double_click_checkbox(0)

        # Assert
        checkboxes_page.verify_checkbox_is_unchecked(0)

    @allure.story("Double Click")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Double-clicking a checked checkbox leaves it checked")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_double_click_leaves_checked_checkbox_unchanged(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify double-clicking a checked checkbox leaves it checked."""
        # Arrange
        checkboxes_page.navigate()
        checkboxes_page.check_checkbox(0)

        # Act
        checkboxes_page.double_click_checkbox(0)

        # Assert
        checkboxes_page.verify_checkbox_is_checked(0)

    @allure.story("Page Reload")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Checkbox state resets to default after page reload")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_state_resets_to_default_after_reload(
        self,
        checkboxes_page: CheckboxesPage,
    ) -> None:
        """Verify both checkboxes revert to their default state after a page reload."""
        # Arrange
        checkboxes_page.navigate()
        checkboxes_page.check_checkbox(0)
        checkboxes_page.uncheck_checkbox(1)

        # Act
        checkboxes_page.reload()

        # Assert
        checkboxes_page.verify_initial_state()
