"""Selector constants for The Internet pages."""

# ── Shared (present on every The Internet page) ──────────────────────────────
PAGE_HEADING = "h3"
GITHUB_FORK_LINK = "a[href='https://github.com/tourdedave/the-internet']"
GITHUB_FORK_IMAGE = "a[href='https://github.com/tourdedave/the-internet'] img"
PAGE_FOOTER = "#page-footer"
FOOTER_LINK = "#page-footer a"

# ── Add/Remove Elements ──────────────────────────────────────────────────────
ADD_ELEMENT_BUTTON = "button[onclick='addElement()']"
DELETE_BUTTON = ".added-manually"

# ── Basic Auth ────────────────────────────────────────────────────────────────
BASIC_AUTH_SUCCESS_MESSAGE = "#content .example p"
