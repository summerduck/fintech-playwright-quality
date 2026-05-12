# https://docs.stripe.com/testing

from config.data.models import Card


class TestCard:
    """Card factories for Accept a Payment tests.

    Each method returns an immutable Card instance with all fields
    needed to complete the payment form.
    """

    @staticmethod
    def _make(
        number: str,
        *,
        cvc: str = "123",
        requires_3ds: bool = False,
    ) -> "Card":
        return Card(
            number=number,
            name="John Doe",
            cvc=cvc,
            expiration_date="12/34",
            zip_code="12345",
            requires_3ds=requires_3ds,
        )

    # ── Successful payments by brand ─────────────────────────────────────

    @staticmethod
    def visa() -> "Card":
        return TestCard._make("4242 4242 4242 4242")

    @staticmethod
    def visa_debit() -> "Card":
        return TestCard._make("4000 0566 5566 5556")

    @staticmethod
    def mastercard() -> "Card":
        return TestCard._make("5555 5555 5555 4444")

    @staticmethod
    def mastercard_debit() -> "Card":
        return TestCard._make("5200 8282 8282 8210")

    @staticmethod
    def mastercard_prepaid() -> "Card":
        return TestCard._make("5105 1051 0510 5100")

    @staticmethod
    def amex() -> "Card":
        return TestCard._make("3782 8224 6310 005", cvc="1234")

    @staticmethod
    def discover() -> "Card":
        return TestCard._make("6011 1111 1111 1117")

    @staticmethod
    def diners_club() -> "Card":
        return TestCard._make("3056 9300 0902 0004")

    @staticmethod
    def jcb() -> "Card":
        return TestCard._make("3566 0020 2036 0505")

    @staticmethod
    def unionpay() -> "Card":
        return TestCard._make("6200 0000 0000 0005")

    # ── Declined payments ────────────────────────────────────────────────

    @staticmethod
    def generic_decline() -> "Card":
        """card_declined / generic_decline."""
        return TestCard._make("4000 0000 0000 0002")

    @staticmethod
    def insufficient_funds() -> "Card":
        """card_declined / insufficient_funds."""
        return TestCard._make("4000 0000 0000 9995")

    @staticmethod
    def lost_card() -> "Card":
        """card_declined / lost_card."""
        return TestCard._make("4000 0000 0000 9987")

    @staticmethod
    def stolen_card() -> "Card":
        """card_declined / stolen_card."""
        return TestCard._make("4000 0000 0000 9979")

    @staticmethod
    def expired_card() -> "Card":
        """expired_card error regardless of the expiry entered."""
        return TestCard._make("4000 0000 0000 0069")

    @staticmethod
    def incorrect_cvc() -> "Card":
        """incorrect_cvc error when a CVC is provided."""
        return TestCard._make("4000 0000 0000 0127")

    @staticmethod
    def processing_error() -> "Card":
        """processing_error decline."""
        return TestCard._make("4000 0000 0000 0119")

    # ── 3D Secure ────────────────────────────────────────────────────────

    @staticmethod
    def three_ds_authenticate_unless_setup() -> "Card":
        """Requires 3DS challenge on-session; skipped after off-session setup."""
        return TestCard._make("4000 0025 0000 3155", requires_3ds=True)

    @staticmethod
    def three_ds_always_authenticate() -> "Card":
        """Requires 3DS on every transaction regardless of setup."""
        return TestCard._make("4000 0027 6000 3184", requires_3ds=True)

    @staticmethod
    def three_ds_required() -> "Card":
        """3DS required; payment succeeds after authentication."""
        return TestCard._make("4000 0000 0000 3220", requires_3ds=True)


# ── Invalid field constants for form validation tests ────────────────────

INVALID_CARD_NUMBER = "1234567890123456"  # fails Luhn check
EMPTY_EXPIRY = ""
PAST_EXPIRY = "01/20"  # January 2020
INCOMPLETE_CVC = "12"
