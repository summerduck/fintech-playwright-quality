"""Tests for Drag and Drop on The Internet."""

import logging

import allure
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from pages.the_internet.drag_and_drop_page import DragAndDropPage

logger = logging.getLogger(__name__)

_PROPERTY_SETTINGS = {
    "max_examples": 20,
    "suppress_health_check": [HealthCheck.function_scoped_fixture],
    # Browser interactions exceed Hypothesis's default 200 ms deadline.
    "deadline": None,
}


@allure.epic("The Internet")
@allure.feature("Drag and Drop")
class TestDragAndDrop:
    """Drag and Drop test suite for The Internet."""

    @allure.story("Page structure")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Drag and Drop page loads with heading and both columns")
    @pytest.mark.theinternet
    @pytest.mark.smoke
    def test_page_loads_correctly(
        self,
        drag_and_drop_page: DragAndDropPage,
    ) -> None:
        """Verify the page heading and both columns are visible on load."""
        # Arrange
        drag_and_drop_page.navigate()

        # Act & Assert
        drag_and_drop_page.verify_page_loaded()

    @allure.story("Drag column A to B")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Dragging column A onto column B swaps their positions")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_drag_column_a_to_b_swaps_columns(
        self,
        drag_and_drop_page: DragAndDropPage,
    ) -> None:
        """Verify that dragging A onto B results in B first, A second."""
        # Arrange
        drag_and_drop_page.navigate()
        drag_and_drop_page.verify_columns_in_default_order()

        # Act
        drag_and_drop_page.drag_column_a_to_b()

        # Assert
        drag_and_drop_page.verify_columns_swapped()

    @allure.story("Drag column B to A")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Dragging column B onto column A swaps their positions")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_drag_column_b_to_a_swaps_columns(
        self,
        drag_and_drop_page: DragAndDropPage,
    ) -> None:
        """Verify that dragging B onto A results in B first, A second."""
        # Arrange
        drag_and_drop_page.navigate()
        drag_and_drop_page.verify_columns_in_default_order()

        # Act
        drag_and_drop_page.drag_column_b_to_a()

        # Assert
        drag_and_drop_page.verify_columns_swapped()

    @allure.story("Double drag restores order")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Dragging A to B then B to A restores the original column order")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_drag_twice_restores_original_order(
        self,
        drag_and_drop_page: DragAndDropPage,
    ) -> None:
        """Verify that two sequential drags restore the original order."""
        # Arrange
        drag_and_drop_page.navigate()

        # Act
        drag_and_drop_page.drag_column_a_to_b()
        drag_and_drop_page.drag_column_b_to_a()

        # Assert
        drag_and_drop_page.verify_columns_in_default_order()

    @allure.story("Property: odd drag count swaps columns")
    @allure.title("An odd number of drags always leaves columns swapped")
    @pytest.mark.theinternet
    @pytest.mark.property
    @settings(**_PROPERTY_SETTINGS)
    @given(n=st.integers(min_value=1, max_value=7).filter(lambda x: x % 2 == 1))
    def test_odd_number_of_drags_swaps_columns(
        self,
        drag_and_drop_page: DragAndDropPage,
        n: int,
    ) -> None:
        """Property: any odd number of A→B drags leaves B first, A second.

        Invariant: ∀ n odd ∈ [1, 7]: drag_a_to_b(n) → columns swapped
        """
        drag_and_drop_page.navigate()
        drag_and_drop_page.drag_column_a_to_b(n)
        drag_and_drop_page.verify_columns_swapped()

    @allure.story("Property: even drag count restores order")
    @allure.title("An even number of drags always restores the original column order")
    @pytest.mark.theinternet
    @pytest.mark.property
    @settings(**_PROPERTY_SETTINGS)
    @given(n=st.integers(min_value=2, max_value=8).filter(lambda x: x % 2 == 0))
    def test_even_number_of_drags_restores_original_order(
        self,
        drag_and_drop_page: DragAndDropPage,
        n: int,
    ) -> None:
        """Property: any even number of A→B drags restores the default order.

        Invariant: ∀ n even ∈ [2, 8]: drag_a_to_b(n) → default order
        """
        drag_and_drop_page.navigate()
        drag_and_drop_page.drag_column_a_to_b(n)
        drag_and_drop_page.verify_columns_in_default_order()
