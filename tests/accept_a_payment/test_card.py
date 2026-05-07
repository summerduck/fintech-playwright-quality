"""
AUT: custom-payment-flow/client/html/card.html
"""

import logging

import allure
import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from config.data.models import Card
from config.data.card_messages import CardMessages
from config.data.test_cards import TestCard
from pages.accept_a_payment.card_page import CardPage
from pages.accept_a_payment.three_ds_page import ThreeDSPage

logger = logging.getLogger(__name__)


@allure.feature("Card")
@allure.epic("Page Load & Initial State")
@pytest.mark.acceptapayment
class TestPageLoadAndInitialState:
    """Card test suite for Card Page Load & Initial State."""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Card page loads successfully")
    @pytest.mark.smoke
    def test_page_load_and_initial_state(self, card_page: CardPage) -> None:
        """Test card page loads successfully."""
        pass


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
                TestCard.three_ds_authenticate_unless_setup(),
                id="3ds",
            ),
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
        self, card_page: CardPage, three_ds_page: ThreeDSPage, card: Card
    ) -> None:
        """Fill the card form and complete payment for the given card."""
        # Act & Assert
        card_page.navigate()
        card_page.fill_card_form(card)
        card_page.click_pay_button()
        three_ds_page.handle_three_ds(card.requires_3ds)
        card_page.verify_messages_contain_text(CardMessages.PAYMENT_SUCCEEDED_PREFIX)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(
        "Payment Intent ID appears as a dashboard link in #messages after successful payment"
    )
    def test_payment_succeeded_and_dashboard_link_is_visible(
        self,
        card_page: CardPage,
        card: Card = TestCard.visa(),
    ) -> None:
        """
        After successful payment, payment intent ID appears as a link to the Stripe dashboard.
        """
        card_page.navigate()
        card_page.fill_card_form(card)
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.PAYMENT_SUCCEEDED_PREFIX)
        card_page.verify_dashboard_link_is_visible()
        card_page.get_dashboard_link()
        card_page.get_payment_id()


@allure.epic("Accept a Payment")
@allure.feature("Card")
@allure.story("Form Validation")
@pytest.mark.acceptapayment
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
        card: Card = TestCard.visa()
        card_page.navigate()
        card_page.fill_name(card.name)
        card_page.fill_card_number("1234567890123456")
        card_page.fill_cvc(card.cvc)
        card_page.fill_expiration_date(card.expiration_date)
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.CARD_NUMBER_INVALID)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Form validation - invalid card format")
    def test_form_validation_expiration_date_incomplete(
        self,
        card_page: CardPage,
    ) -> None:
        """Test form validation: invalid card number."""
        card: Card = TestCard.visa()
        card_page.navigate()
        card_page.fill_name(card.name)
        card_page.fill_card_number(card.number)
        card_page.fill_cvc(card.cvc)
        card_page.fill_expiration_date("")
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.EXPIRY_INCOMPLETE)

    def test_form_validation_expiration_date_in_past(
        self,
        card_page: CardPage,
    ) -> None:
        """Test form validation: invalid expiration date month."""
        card: Card = TestCard.visa()
        card_page.navigate()
        card_page.fill_name(card.name)
        card_page.fill_card_number(card.number)
        card_page.fill_cvc(card.cvc)
        card_page.fill_expiration_date("01/20")
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.EXPIRY_IN_PAST)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Form validation - incomplete CVC")
    def test_form_validation_cvc_incomplete(
        self,
        card_page: CardPage,
    ) -> None:
        """Test form validation: CVC field left empty."""
        card: Card = TestCard.visa()
        card_page.navigate()
        card_page.fill_name(card.name)
        card_page.fill_card_number(card.number)
        card_page.fill_cvc("12")
        card_page.fill_expiration_date(card.expiration_date)
        card_page.fill_zip(card.zip_code)
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.CVC_INCOMPLETE)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Form validation - incomplete ZIP code")
    def test_form_validation_zip_incomplete(
        self,
        card_page: CardPage,
    ) -> None:
        """Test form validation: ZIP/postal code field left empty."""
        card: Card = TestCard.visa()
        card_page.navigate()
        card_page.fill_name(card.name)
        card_page.fill_card_number(card.number)
        card_page.fill_cvc(card.cvc)
        card_page.fill_expiration_date(card.expiration_date)
        card_page.click_pay_button()
        card_page.verify_messages_contain_text(CardMessages.ZIP_INCOMPLETE)
