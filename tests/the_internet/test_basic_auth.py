"""Tests for Basic Auth on The Internet."""

import logging
import string

import allure
import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from config.data.models import User
from config.data.the_internet import TheInternetUser
from pages.the_internet.basic_auth_page import BasicAuthPage

logger = logging.getLogger(__name__)

_PROPERTY_SETTINGS = {
    "max_examples": 20,
    "suppress_health_check": [HealthCheck.function_scoped_fixture],
    # Browser interactions exceed Hypothesis's default 200 ms deadline.
    "deadline": None,
}
# Safe ASCII alphabet: avoids control chars and newlines that could
# corrupt HTTP Authorization headers.
_CRED_STRATEGY = st.text(
    alphabet=string.ascii_letters + string.digits + "_-",
    min_size=1,
    max_size=50,
)


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
    ) -> None:
        """Verify that valid HTTP Basic Auth credentials grant access."""
        # Arrange
        basic_auth_page.set_credentials(TheInternetUser.valid())

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
    ) -> None:
        """Verify the success message mentions congratulations and credentials."""
        # Arrange
        basic_auth_page.set_credentials(TheInternetUser.valid())

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
    ) -> None:
        """Verify the complete page structure after successful authentication."""
        # Arrange
        basic_auth_page.set_credentials(TheInternetUser.valid())

        # Act
        basic_auth_page.navigate()

        # Assert
        basic_auth_page.verify_page_loaded()
        basic_auth_page.verify_footer_visible()

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

    @allure.story("Property: invalid credentials")
    @allure.title("Any non-admin credentials always return 401 Unauthorized")
    @pytest.mark.theinternet
    @pytest.mark.property
    @pytest.mark.security
    @settings(**_PROPERTY_SETTINGS)
    @given(username=_CRED_STRATEGY, password=_CRED_STRATEGY)
    def test_any_invalid_credentials_return_401(
        self,
        basic_auth_page: BasicAuthPage,
        username: str,
        password: str,
    ) -> None:
        """Property: any credential pair except the valid one returns 401.

        Invariant: ∀ (u, p) ≠ ("admin", "admin"): status == 401
        """
        assume(not (username == "admin" and password == "admin"))
        basic_auth_page.set_credentials(User(username=username, password=password))
        basic_auth_page.navigate_and_verify_unauthorized()

    @allure.story("Property: wrong password")
    @allure.title("Any wrong password for valid username always returns 401")
    @pytest.mark.theinternet
    @pytest.mark.property
    @pytest.mark.security
    @settings(**_PROPERTY_SETTINGS)
    @given(password=_CRED_STRATEGY)
    def test_wrong_password_for_valid_user_returns_401(
        self,
        basic_auth_page: BasicAuthPage,
        password: str,
    ) -> None:
        """Property: correct username with any wrong password returns 401.

        Invariant: ∀ p ≠ "admin": User("admin", p) → status == 401
        """
        assume(password != "admin")
        basic_auth_page.set_credentials(User(username="admin", password=password))
        basic_auth_page.navigate_and_verify_unauthorized()
