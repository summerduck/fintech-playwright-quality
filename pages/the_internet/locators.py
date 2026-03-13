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

# ── Drag and Drop ─────────────────────────────────────────────────────────────
DRAG_DROP_COLUMN_A = "#column-a"
DRAG_DROP_COLUMN_B = "#column-b"
DRAG_DROP_COLUMN_A_HEADER = "#column-a header"
DRAG_DROP_COLUMN_B_HEADER = "#column-b header"
DRAG_DROP_FIRST_COLUMN_HEADER = "#columns .column:first-child header"
DRAG_DROP_SECOND_COLUMN_HEADER = "#columns .column:last-child header"

# ── Broken Images ─────────────────────────────────────────────────────────────
BROKEN_IMAGES_CONTENT_IMAGES = "div.example img"

# ── Checkboxes ────────────────────────────────────────────────────────────────
CHECKBOXES_CHECKBOX = "input[type='checkbox']"
