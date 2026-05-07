"""
 Test Plan: card.html — Stripe Card Payment Flow

 AUT: custom-payment-flow/client/html/card.html

 Coverage areas:
  1. Page Load & Initial State
  2. Static Content & UI Structure
  3. Accessibility
  4. Navigation
  5. Happy Path — Successful Payment (Visa & Mastercard)
  6. 3D Secure Authentication Flow
  7. Card Decline Error Handling
  8. Client-Side Form Validation
  9. Double Submission Prevention
 10. Backend API Failure Handling
 11. Visual Regression (snapshot)
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


@allure.epic("Accept a Payment")
@allure.feature("Card")
@pytest.mark.acceptapayment
class TestCardFlow:
    """Card test suite for Accept a Payment."""

    @allure.story("Actions")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Fill the name input with the given name")
    @pytest.mark.smoke
    def test_fill_card_form_and_complete_payment(
        self,
        card_page: CardPage,
        three_ds_page: ThreeDSPage,
    ) -> None:
        """Fill the card form and complete payment for the given card."""
        # Act & Assert
        card: Card = TestCard.three_ds_authenticate_unless_setup()
        card_page.navigate()
        card_page.fill_name(card.name)
        card_page.fill_card_number(card.number)
        card_page.fill_cvc(card.cvc)
        card_page.fill_expiration_date(card.expiration_date)
        card_page.fill_zip(card.zip_code)
        card_page.click_pay_button()
        if card.requires_3ds:
            three_ds_page.wait_for_three_ds_frame()
            three_ds_page.click_three_ds_fail_button()
            three_ds_page.wait_for_three_ds_frame_to_be_hidden()
        card_page.verify_messages_contain_text(CardMessages.PAYMENT_SUCCEEDED_PREFIX)


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
