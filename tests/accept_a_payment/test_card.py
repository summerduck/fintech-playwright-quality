"""
AUT: custom-payment-flow/client/html/card.html
"""

import logging

import allure
import pytest

from config.data.card_messages import CardMessages
from config.data.models import Card
from config.data.test_cards import (
    EMPTY_EXPIRY,
    INCOMPLETE_CVC,
    INVALID_CARD_NUMBER,
    PAST_EXPIRY,
    TestCard,
)
from pages.accept_a_payment.card_page import CardPage

logger = logging.getLogger(__name__)


@allure.feature("Card")
@allure.epic("Page Load & Initial State")
@pytest.mark.acceptapayment
@pytest.mark.regression
class TestPageLoadAndInitialState:
    """Card test suite for Card Page Load & Initial State."""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Navigates directly to card.html and returns 200")
    def test_card_page_direct_navigation_status_200(self, card_page: CardPage) -> None:
        """Goto card.html and assert status 200."""
        card_page.navigate()
        card_page.verify_response_status()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title('Page title is "Card"')
    def test_page_title_is_card(self, card_page: CardPage) -> None:
        """Goto card.html and assert page title is 'Card'."""
        card_page.navigate()
        card_page.verify_page_title_is_card()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Stripe card element iframe is mounted within #card-element")
    def test_stripe_card_element_iframe_visible(self, card_page: CardPage) -> None:
        """Goto card.html and assert Stripe iframe in #card-element."""
        card_page.navigate()
        card_page.verify_stripe_card_element_iframe_visible()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("#messages panel is hidden on load")
    def test_messages_panel_hidden_on_load(self, card_page: CardPage) -> None:
        """Goto card.html and assert #messages is hidden on load."""
        card_page.navigate()
        card_page.verify_messages_panel_is_hidden()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("#card-errors is empty on load")
    def test_card_errors_empty_on_load(self, card_page: CardPage) -> None:
        """Goto card.html and assert #card-errors is empty."""
        card_page.navigate()
        card_page.verify_card_errors_are_empty_on_load()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Pay button is enabled on load")
    def test_pay_button_enabled_on_load(self, card_page: CardPage) -> None:
        """Goto card.html and assert #submit/pay button is enabled."""
        card_page.navigate()
        card_page.verify_pay_button_is_enabled_on_load()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title('Name input is pre-filled with "Jenny Rosen"')
    def test_name_input_prefilled_jenny_rosen(self, card_page: CardPage) -> None:
        """Goto card.html and assert #name input value is 'Jenny Rosen'."""
        card_page.navigate()
        card_page.verify_name_input_prefilled_jenny_rosen()


@allure.feature("Card")
@allure.epic("Happy Path — Successful Payment")
@pytest.mark.acceptapayment
class TestSuccessfulPayment:
    """Card test suite for Card Happy Path — Successful Payment."""

    @allure.story("Actions")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Fill the card form and complete payment for the given card")
    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "card",
        [
            pytest.param(
                TestCard.visa(),
                id="visa",
            ),
            pytest.param(
                TestCard.mastercard(),
                id="mastercard",
            ),
        ],
    )
    def test_fill_card_form_and_complete_payment(
        self,
        card_page: CardPage,
        card: Card,
    ) -> None:
        """Fill the card form and complete payment for the given card."""
        card_page.navigate()
        card_page.fill_card_form(card)
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.PAYMENT_SUCCEEDED_PREFIX)

    @allure.story("Actions")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(
        "Payment Intent ID appears as a dashboard link in #messages after successful payment"
    )
    @pytest.mark.regression
    def test_payment_succeeded_and_dashboard_link_is_visible(
        self,
        card_page: CardPage,
    ) -> None:
        """
        After successful payment, payment intent ID appears as a link to the Stripe dashboard.
        """
        card = TestCard.visa()
        card_page.navigate()
        card_page.fill_card_form(card)
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.PAYMENT_SUCCEEDED_PREFIX)
        card_page.verify_dashboard_link_is_visible()
        card_page.get_dashboard_link()
        card_page.get_payment_id()


@allure.feature("Card")
@allure.epic("3D Secure Authentication Flow")
@pytest.mark.acceptapayment
class Test3DSecureAuthenticationFlow:
    """Card test suite for Card 3D Secure Authentication Flow."""

    @allure.story("Actions")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(
        "Fill the card form and complete payment for the given card with 3DS authentication"
    )
    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "card",
        [
            pytest.param(
                TestCard.mastercard(),
                id="mastercard",
            ),
        ],
    )
    def test_fill_card_form_and_complete_payment_with_3ds_authentication(
        self,
        card_page: CardPage,
        card: Card,
    ) -> None:
        """Fill the card form and complete payment for the given card."""
        card_page.navigate()
        card_page.fill_card_form(card)
        card_page.click_pay_button()
        card_page.handle_three_ds(card.requires_3ds)
        card_page.verify_messages_contain_text(CardMessages.PAYMENT_SUCCEEDED_PREFIX)


@allure.epic("Accept a Payment")
@allure.feature("Card")
@allure.story("Form Validation")
@pytest.mark.acceptapayment
@pytest.mark.regression
class TestCardFormValidation:
    """Card test suite for Accept a Payment."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Form validation - empty fields, invalid card format, expired date")
    def test_form_validation_card_number_incomplete(
        self,
        card_page: CardPage,
    ) -> None:
        """Test form validation: empty fields, invalid card number, expired date."""
        card_page.navigate()
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.CARD_NUMBER_INCOMPLETE)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Form validation - invalid card format")
    def test_form_validation_card_number_invalid(
        self,
        card_page: CardPage,
    ) -> None:
        """Test form validation: invalid card number."""
        visa_card = TestCard.visa()
        card_page.navigate()
        card_page.fill_name(visa_card.name)
        card_page.fill_card_number(INVALID_CARD_NUMBER)
        card_page.fill_cvc(visa_card.cvc)
        card_page.fill_expiration_date(visa_card.expiration_date)
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.CARD_NUMBER_INVALID)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Form validation - incomplete expiration date")
    def test_form_validation_expiration_date_incomplete(
        self,
        card_page: CardPage,
    ) -> None:
        """Test form validation: expiration date field left empty."""
        visa_card = TestCard.visa()
        card_page.navigate()
        card_page.fill_name(visa_card.name)
        card_page.fill_card_number(visa_card.number)
        card_page.fill_cvc(visa_card.cvc)
        card_page.fill_expiration_date(EMPTY_EXPIRY)
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.EXPIRY_INCOMPLETE)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Form validation - invalid expiration date month")
    def test_form_validation_expiration_date_in_past(
        self,
        card_page: CardPage,
    ) -> None:
        """Test form validation: invalid expiration date month."""
        visa_card = TestCard.visa()
        card_page.navigate()
        card_page.fill_name(visa_card.name)
        card_page.fill_card_number(visa_card.number)
        card_page.fill_cvc(visa_card.cvc)
        card_page.fill_expiration_date(PAST_EXPIRY)
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.EXPIRY_IN_PAST)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Form validation - incomplete CVC")
    def test_form_validation_cvc_incomplete(
        self,
        card_page: CardPage,
    ) -> None:
        """Test form validation: CVC field left empty."""
        visa_card = TestCard.visa()
        card_page.navigate()
        card_page.fill_name(visa_card.name)
        card_page.fill_card_number(visa_card.number)
        card_page.fill_cvc(INCOMPLETE_CVC)
        card_page.fill_expiration_date(visa_card.expiration_date)
        card_page.fill_zip(visa_card.zip_code)
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.CVC_INCOMPLETE)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Form validation - incomplete ZIP code")
    def test_form_validation_zip_incomplete(
        self,
        card_page: CardPage,
    ) -> None:
        """Test form validation: ZIP/postal code field left empty."""
        visa_card = TestCard.visa()
        card_page.navigate()
        card_page.fill_name(visa_card.name)
        card_page.fill_card_number(visa_card.number)
        card_page.fill_cvc(visa_card.cvc)
        card_page.fill_expiration_date(visa_card.expiration_date)
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.ZIP_INCOMPLETE)
