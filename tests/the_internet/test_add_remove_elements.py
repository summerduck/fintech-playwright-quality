"""Tests for Add/Remove Elements on The Internet."""

import logging

import allure
import pytest

from pages.the_internet.add_remove_elements_page import AddRemoveElementsPage

logger = logging.getLogger(__name__)


@allure.epic("The Internet")
@allure.feature("Add/Remove Elements")
class TestAddRemoveElements:
    """Add/Remove Elements test suite for The Internet."""

    @allure.story("Page structure")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Add/Remove Elements page loads with heading and button")
    @pytest.mark.theinternet
    @pytest.mark.smoke
    def test_page_loads_correctly(
        self,
        add_remove_elements_page: AddRemoveElementsPage,
    ) -> None:
        """Verify the page heading and Add Element button are visible."""
        # Arrange
        add_remove_elements_page.navigate()

        # Act & Assert
        add_remove_elements_page.verify_page_loaded()

    @allure.story("Add element")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Clicking Add Element creates one Delete button")
    @pytest.mark.theinternet
    @pytest.mark.smoke
    def test_add_single_element(
        self,
        add_remove_elements_page: AddRemoveElementsPage,
    ) -> None:
        """Verify a single Delete button appears after clicking Add Element."""
        # Arrange
        add_remove_elements_page.navigate()

        # Act
        add_remove_elements_page.click_add_element()

        # Assert
        add_remove_elements_page.verify_delete_button_count(1)

    @allure.story("Add element")
    @pytest.mark.theinternet
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "count",
        [
            pytest.param(2, id="two-elements"),
            pytest.param(5, id="five-elements"),
        ],
    )
    def test_add_multiple_elements(
        self,
        add_remove_elements_page: AddRemoveElementsPage,
        count: int,
    ) -> None:
        """Verify the correct number of Delete buttons after adding N elements."""
        allure.dynamic.title(
            f"Clicking Add Element {count} times creates {count} Delete buttons"
        )
        allure.dynamic.severity(allure.severity_level.NORMAL)

        # Arrange
        add_remove_elements_page.navigate()

        # Act
        for _ in range(count):
            add_remove_elements_page.click_add_element()

        # Assert
        add_remove_elements_page.verify_delete_button_count(count)

    @allure.story("Remove element")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Clicking Delete removes the element")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_remove_single_element(
        self,
        add_remove_elements_page: AddRemoveElementsPage,
    ) -> None:
        """Verify a Delete button is removed after clicking it."""
        # Arrange
        add_remove_elements_page.navigate()
        add_remove_elements_page.click_add_element()

        # Act
        add_remove_elements_page.click_delete_element()

        # Assert
        add_remove_elements_page.verify_delete_button_count(0)

    @allure.story("Remove element")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("All Delete buttons can be removed individually")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_remove_all_elements(
        self,
        add_remove_elements_page: AddRemoveElementsPage,
    ) -> None:
        """Verify all added elements can be removed one by one."""
        # Arrange
        add_remove_elements_page.navigate()
        for _ in range(3):
            add_remove_elements_page.click_add_element()

        # Act
        for _ in range(3):
            add_remove_elements_page.click_delete_element()

        # Assert
        add_remove_elements_page.verify_delete_button_count(0)

    @allure.story("Add and remove elements")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Adding elements after removing keeps correct count")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_add_element_after_removing(
        self,
        add_remove_elements_page: AddRemoveElementsPage,
    ) -> None:
        """Verify the count is correct after a mix of add and remove actions."""
        # Arrange
        add_remove_elements_page.navigate()
        add_remove_elements_page.click_add_element()
        add_remove_elements_page.click_add_element()

        # Act
        add_remove_elements_page.click_delete_element()
        add_remove_elements_page.click_add_element()

        # Assert
        add_remove_elements_page.verify_delete_button_count(2)
