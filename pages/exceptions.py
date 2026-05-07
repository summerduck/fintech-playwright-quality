"""Domain exceptions for Stripe payment flow test automation."""


class StripeTestError(Exception):
    """Base class for all Stripe test automation exceptions."""


class NavigationError(StripeTestError):
    """Raised when a page returns a non-200 HTTP status on navigation."""


class StripeIframeError(StripeTestError):
    """Raised when the Stripe card element iframe fails to mount or become visible."""


class PaymentDeclinedError(StripeTestError):
    """Raised when Stripe declines the payment (e.g. insufficient funds, card blocked)."""


class ThreeDSAuthenticationError(StripeTestError):
    """Raised when 3DS authentication does not complete as expected."""


class CardValidationError(StripeTestError):
    """Raised when client-side card field validation fails (incomplete number, bad CVC, etc.)."""
