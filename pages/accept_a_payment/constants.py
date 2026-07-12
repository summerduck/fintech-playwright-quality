"""Shared constants for the Accept a Payment page objects."""

# Stripe payment confirmation and 3DS challenge can take noticeably longer
# than a normal UI interaction, so payment-flow waits get their own budget.
PAYMENT_TIMEOUT = 30_000
