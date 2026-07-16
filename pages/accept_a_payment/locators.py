"""Selector constants for Accept a Payment pages."""

PAGE_HEADING = "h1"


# ── Card Page ───────────────────────────────────────────────────────────────

CARD_FORM = "#payment-form"
NAME_INPUT = "#name"
CARD_ELEMENT = "#card-element"
CARD_ERRORS = "#card-errors"
PAY_BUTTON = "#submit"
MESSAGES = "#messages"
# Stripe injects these iframe inputs with [name] attributes only — no accessible roles exposed.
CARD_INPUT = "[name='cardnumber']"
CVC_INPUT = "[name='cvc']"
EXPIRATION_DATE_INPUT = "[name='exp-date']"
ZIP_INPUT = "[name='postal']"
DASHBOARD_LINK = "[href*='dashboard.stripe.com']"

# ── 3DS Frame ───────────────────────────────────────────────────────────

# Stripe.js injects an outer wrapper iframe for the 3DS redirect flow;
# #challengeFrame lives inside it, not in the main document.
THREE_DS_WRAPPER_FRAME = "iframe[src*='js.stripe.com/v3/three-ds-2-challenge']"
THREE_DS_FRAME = "#challengeFrame"
THREE_DS_FAIL_BUTTON = "#test-source-fail-3ds"
THREE_DS_COMPLETE_BUTTON = "#test-source-authorize-3ds"
