"""Pytest fixtures for The Internet tests.

Provides page object fixtures so tests receive ready-to-use page
instances without instantiating them directly. Each page fixture
resolves its own base URL from the page's ``APP_NAME`` and the
session-scoped ``env`` fixture.
"""

import pytest
from playwright.sync_api import Page

from config import get_base_url
from pages.the_internet.add_remove_elements_page import AddRemoveElementsPage
from pages.the_internet.basic_auth_page import BasicAuthPage
from pages.the_internet.drag_and_drop_page import DragAndDropPage


@pytest.fixture
def add_remove_elements_page(page: Page, env: str) -> AddRemoveElementsPage:
    """Provide an AddRemoveElementsPage instance for the current test."""
    base_url = get_base_url(AddRemoveElementsPage.APP_NAME, env)
    return AddRemoveElementsPage(page, base_url)


@pytest.fixture
def basic_auth_page(page: Page, env: str) -> BasicAuthPage:
    """Provide a BasicAuthPage instance for the current test."""
    base_url = get_base_url(BasicAuthPage.APP_NAME, env)
    return BasicAuthPage(page, base_url)


@pytest.fixture
def drag_and_drop_page(page: Page, env: str) -> DragAndDropPage:
    """Provide a DragAndDropPage instance for the current test."""
    base_url = get_base_url(DragAndDropPage.APP_NAME, env)
    return DragAndDropPage(page, base_url)
