"""Tests for Basic Auth on The Internet."""

import logging

import allure
import pytest

from config.data.models import User
from pages.the_internet.basic_auth_page import BasicAuthPage

logger = logging.getLogger(__name__)


@allure.epic("The Internet")
@allure.feature("Basic Auth")
class TestBasicAuth:
    """Basic Auth test suite for The Internet."""

    @allure.story("Successful authentication")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Valid credentials grant access to the protected page")
    @pytest.mark.theinternet
    @pytest.mark.smoke
    def test_successful_auth_with_valid_credentials(
        self,
        basic_auth_page: BasicAuthPage,
        valid_auth_user: User,
    ) -> None:
        """Verify that valid HTTP Basic Auth credentials grant access."""
        # Arrange
        basic_auth_page.set_credentials(valid_auth_user)

        # Act
        basic_auth_page.navigate()

        # Assert
        basic_auth_page.verify_successful_auth()

    @allure.story("Successful authentication")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Success message confirms correct credentials")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_success_message_content(
        self,
        basic_auth_page: BasicAuthPage,
        valid_auth_user: User,
    ) -> None:
        """Verify the success message mentions congratulations and credentials."""
        # Arrange
        basic_auth_page.set_credentials(valid_auth_user)

        # Act
        basic_auth_page.navigate()

        # Assert
        basic_auth_page.verify_success_message_content()

    @allure.story("Page structure")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Authenticated page displays heading, message, and footer")
    @pytest.mark.theinternet
    @pytest.mark.regression
    def test_page_structure_after_auth(
        self,
        basic_auth_page: BasicAuthPage,
        valid_auth_user: User,
    ) -> None:
        """Verify the complete page structure after successful authentication."""
        # Arrange
        basic_auth_page.set_credentials(valid_auth_user)

        # Act
        basic_auth_page.navigate()

        # Assert
        basic_auth_page.verify_page_loaded()
        basic_auth_page.verify_footer_visible()

    @allure.story("Failed authentication")
    @pytest.mark.theinternet
    @pytest.mark.security
    @pytest.mark.parametrize(
        "user",
        [
            pytest.param(
                User(username="wrong_user", password="wrong_pass"),
                id="both-invalid",
            ),
            pytest.param(
                User(username="admin", password="wrong_pass"),
                id="wrong-password",
            ),
            pytest.param(
                User(username="wrong_user", password="admin"),
                id="wrong-username",
            ),
        ],
    )
    def test_unauthorized_with_invalid_credentials(
        self,
        basic_auth_page: BasicAuthPage,
        user: User,
    ) -> None:
        """Verify that invalid credentials return HTTP 401."""
        allure.dynamic.title(
            f"Invalid credentials (user '{user}') return 401 Unauthorized"
        )
        allure.dynamic.severity(allure.severity_level.CRITICAL)

        # Arrange
        basic_auth_page.set_credentials(user)

        # Act & Assert
        basic_auth_page.navigate_and_verify_unauthorized()

    @allure.story("Failed authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Missing credentials return 401 Unauthorized")
    @pytest.mark.theinternet
    @pytest.mark.security
    def test_unauthorized_without_credentials(
        self,
        basic_auth_page: BasicAuthPage,
    ) -> None:
        """Verify that navigating without credentials returns HTTP 401."""
        # Act & Assert
        basic_auth_page.navigate_and_verify_unauthorized()
