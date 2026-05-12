from enum import StrEnum


class CardMessages(StrEnum):
    """Messages that appear in #messages div on card.html.

    Sources:
      - card.js: hardcoded strings from the app
      - Stripe.js: card element validation errors (before submit)
      - Stripe API: decline errors (after confirmCardPayment)
    """

    # ── App messages (card.js) ────────────────────────────────────────────
    NO_PUBLISHABLE_KEY = (
        "No publishable key returned from the server. Please check `.env` and try again"
    )
    CLIENT_SECRET_RETURNED = "Client secret returned."  # nosec B105
    # Payment success — pi_ ID is dynamic, use startswith / contains in assertions
    PAYMENT_SUCCEEDED_PREFIX = "Payment succeeded: pi_"

    # ── Stripe.js validation errors (card element, before submit) ─────────
    # Triggered when required fields are empty or partially filled
    CARD_NUMBER_INCOMPLETE = "Your card number is incomplete."
    CARD_NUMBER_INVALID = "Your card number is invalid."
    EXPIRY_INCOMPLETE = "Your card’s expiry date is incomplete."
    EXPIRY_IN_PAST = "Your card’s expiry year is in the past."
    CVC_INCOMPLETE = "Your card’s security code is incomplete."
    ZIP_INCOMPLETE = "Your postal code is incomplete."

    # ── Stripe decline errors (from bank issuer, after confirmCardPayment) ─
    # Use test cards from https://docs.stripe.com/testing#declined-payments
    CARD_DECLINED = "Your card was declined."
    INSUFFICIENT_FUNDS = "Your card has insufficient funds."
    EXPIRED_CARD = "Your card has expired."
    INCORRECT_CVC = "Your card's security code is incorrect."
    INCORRECT_NUMBER = "The card number is incorrect."
    INCORRECT_ZIP = "Your card's zip code is incorrect."
    LOST_CARD = "Your card was declined."  # same user message as generic decline
    STOLEN_CARD = "Your card was declined."  # same user message as generic decline
    PROCESSING_ERROR = (
        "An error occurred while processing your card. Try again in a little bit."
    )
    CARD_NOT_SUPPORTED = "Your card does not support this type of purchase."
    CURRENCY_NOT_SUPPORTED = "Your card does not support the specified currency."
    DUPLICATE_TRANSACTION = "A transaction with identical amount and credit card information was submitted very recently. Check to see if a recent payment already exists."
    CARD_VELOCITY_EXCEEDED = (
        "You have exceeded the balance or credit limit available on your card."
    )
    AUTHENTICATION_REQUIRED = "This transaction requires authentication."
    DO_NOT_HONOR = "Your card was declined."
    FRAUDULENT = "Your card was declined."
    RESTRICTED_CARD = "Your card has been declined for an unknown reason."
    TESTMODE_DECLINE = "Your card was declined."
