"""Tests for Add/Remove Elements on The Internet."""

import logging

import allure
import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from pages.the_internet.add_remove_elements_page import AddRemoveElementsPage

logger = logging.getLogger(__name__)

_PROPERTY_SETTINGS = {
    "max_examples": 20,
    "suppress_health_check": [HealthCheck.function_scoped_fixture],
    # Browser interactions exceed Hypothesis's default 200 ms deadline.
    "deadline": None,
}


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

    @allure.story("Add and remove elements")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Adding elements after removing keeps correct count")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_add_element_after_removing(
        self,
        add_remove_elements_page: AddRemoveElementsPage,
    ) -> None:
        """Verify the count is correct after interleaved add and remove actions."""
        # Arrange
        add_remove_elements_page.navigate()
        add_remove_elements_page.click_add_element()
        add_remove_elements_page.click_add_element()

        # Act
        add_remove_elements_page.click_delete_element()
        add_remove_elements_page.click_add_element()

        # Assert
        add_remove_elements_page.verify_delete_button_count(2)

    @allure.story("Property: add N")
    @allure.title("Adding N elements always results in exactly N Delete buttons")
    @pytest.mark.theinternet
    @pytest.mark.property
    @settings(**_PROPERTY_SETTINGS)
    @given(count=st.integers(min_value=1, max_value=15))
    def test_add_n_creates_n_delete_buttons(
        self,
        add_remove_elements_page: AddRemoveElementsPage,
        count: int,
    ) -> None:
        """Property: after adding N elements the Delete button count equals N.

        Invariant: ∀ n ∈ [1, 15]: click_add(n) → delete_button_count == n
        """
        add_remove_elements_page.navigate()
        add_remove_elements_page.click_add_element(count)
        add_remove_elements_page.verify_delete_button_count(count)

    @allure.story("Property: add N then remove N")
    @allure.title(
        "Adding then removing all N elements always leaves zero Delete buttons"
    )
    @pytest.mark.theinternet
    @pytest.mark.property
    @settings(**_PROPERTY_SETTINGS)
    @given(count=st.integers(min_value=1, max_value=10))
    def test_add_then_remove_all_leaves_zero(
        self,
        add_remove_elements_page: AddRemoveElementsPage,
        count: int,
    ) -> None:
        """Property: adding then removing all N elements leaves zero Delete buttons.

        Invariant: ∀ n ∈ [1, 10]: click_add(n) → click_delete(n) → count == 0
        """
        add_remove_elements_page.navigate()
        add_remove_elements_page.click_add_element(count)
        add_remove_elements_page.click_delete_element(count=count)
        add_remove_elements_page.verify_delete_button_count(0)

    @allure.story("Property: add A, remove R")
    @allure.title("Final count always equals added minus removed")
    @pytest.mark.theinternet
    @pytest.mark.property
    @settings(**_PROPERTY_SETTINGS)
    @given(
        add=st.integers(min_value=1, max_value=10),
        remove=st.integers(min_value=0, max_value=10),
    )
    def test_final_count_equals_added_minus_removed(
        self,
        add_remove_elements_page: AddRemoveElementsPage,
        add: int,
        remove: int,
    ) -> None:
        """Property: final count == add - remove for any remove in [0, add].

        Invariant: ∀ a ∈ [1, 10], r ∈ [0, a]:
            click_add(a) → click_delete(r) → count == a - r
        """
        assume(remove <= add)
        add_remove_elements_page.navigate()
        add_remove_elements_page.click_add_element(add)
        add_remove_elements_page.click_delete_element(count=remove)
        add_remove_elements_page.verify_delete_button_count(add - remove)
