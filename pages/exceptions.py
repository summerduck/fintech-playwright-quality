"""Domain exceptions for Stripe payment flow test automation."""


class StripeTestError(Exception):
    """Base class for all Stripe test automation exceptions."""


class NavigationError(StripeTestError):
    """Raised when a page returns a non-200 HTTP status on navigation."""
