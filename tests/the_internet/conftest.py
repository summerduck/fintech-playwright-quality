"""Pytest fixtures for The Internet tests.

Provides the base URL and page object fixtures so tests receive
ready-to-use page instances without instantiating them directly.
"""

import pytest
from playwright.sync_api import Page

from pages.the_internet.add_remove_elements_page import AddRemoveElementsPage


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for The Internet application."""
    return "https://the-internet.herokuapp.com"


@pytest.fixture
def add_remove_elements_page(page: Page, base_url: str) -> AddRemoveElementsPage:
    """Provide an AddRemoveElementsPage instance for the current test."""
    return AddRemoveElementsPage(page, base_url)
