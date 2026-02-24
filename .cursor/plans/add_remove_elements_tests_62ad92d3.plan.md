---
name: Add/Remove Elements Tests
overview: Create the full test stack for the Add/Remove Elements page (https://the-internet.herokuapp.com/add_remove_elements/) following the project's 3-tier POM architecture, including BasePage, domain base, concrete page object, locators, conftest fixtures, and test file with Allure annotations.
todos:
  - id: base-page
    content: Write BasePage class in pages/base_page.py (Tier 1)
    status: completed
  - id: init-file
    content: Create pages/the_internet/__init__.py
    status: completed
  - id: locators
    content: Create pages/the_internet/locators.py with Add/Remove Elements selectors
    status: completed
  - id: domain-base
    content: Create pages/the_internet/the_internet_base_page.py (Tier 2)
    status: completed
  - id: page-object
    content: Create pages/the_internet/add_remove_elements_page.py (Tier 3)
    status: completed
  - id: conftest
    content: Update tests/the_internet/conftest.py with page fixture
    status: completed
  - id: tests
    content: Create tests/the_internet/test_add_remove_elements.py with 6 test cases
    status: completed
isProject: false
---

# Add/Remove Elements Test Implementation

## Page Under Test

The page at `/add_remove_elements/` has:

- A heading "Add/Remove Elements"
- An "Add Element" button that appends a "Delete" button each time it is clicked
- Each "Delete" button removes itself when clicked

## Files to Create/Modify

### 1. BasePage -- `pages/base_page.py` (currently empty)

Write the Tier 1 universal base class per the skill template. Provides `navigate()` and `take_screenshot()` methods. All page objects inherit from this.

```python
class BasePage:
    URL_PATH = "/"
    def __init__(self, page: Page, base_url: str) -> None: ...
    def navigate(self) -> Self: ...
    def take_screenshot(self, name: str = "screenshot") -> bytes: ...
```

### 2. Package init -- `pages/the_internet/__init__.py` (missing)

Create an empty `__init__.py` to make `pages/the_internet` a proper Python package.

### 3. Locators -- `pages/the_internet/locators.py` (new)

Module-level `UPPER_SNAKE_CASE` string constants grouped by section: shared elements first, then per-page constants.

```python
# -- Shared (present on every The Internet page)
PAGE_HEADING = "h3"
GITHUB_FORK_LINK = "a[href='https://github.com/touredave/the-internet']"
GITHUB_FORK_IMAGE = "a[href='https://github.com/touredave/the-internet'] img"
PAGE_FOOTER = "#page-footer"
FOOTER_LINK = "#page-footer a"

# -- Add/Remove Elements
ADD_ELEMENT_BUTTON = "button[onclick='addElement()']"
DELETE_BUTTON = ".added-manually"
```

### 4. Tier 2 domain base -- `pages/the_internet/the_internet_base_page.py` (new)

Inherits `BasePage`. Encapsulates the shared UI elements visible on every The Internet page (heading, GitHub fork banner, footer). Locators defined in `__init__`, methods decorated with `@allure.step()`, all return `Self` (except getters).

Methods:

- `get_page_heading()` -> `str` -- returns the `<h3>` heading text
- `get_footer_text()` -> `str` -- returns the footer text content
- `click_github_fork_link()` -> `Self` -- clicks the "Fork me on GitHub" link
- `verify_github_fork_visible()` -> `Self` -- asserts the GitHub fork image is visible
- `verify_footer_visible()` -> `Self` -- asserts the footer with "Powered by Elemental Selenium" is visible

### 5. Tier 3 concrete page -- `pages/the_internet/add_remove_elements_page.py` (new)

Inherits `TheInternetBasePage`. Key methods:

- `click_add_element()` -- clicks the "Add Element" button
- `click_delete_element(index)` -- clicks a specific "Delete" button by index
- `get_delete_button_count()` -- returns the number of "Delete" buttons visible
- `verify_page_loaded()` -- asserts heading and "Add Element" button are visible

All public methods decorated with `@allure.step()`, return `Self` (except getters).

### 6. Update conftest -- [tests/the_internet/conftest.py](tests/the_internet/conftest.py)

Add the `add_remove_elements_page` fixture that provides an `AddRemoveElementsPage` instance.

### 7. Test file -- `tests/the_internet/test_add_remove_elements.py` (new)

Test class `TestAddRemoveElements` with:

- `@allure.epic("The Internet")`, `@allure.feature("Add/Remove Elements")`
- Markers: `@pytest.mark.theinternet` + category marker per test

Test cases:

- **test_page_loads_correctly** (smoke, NORMAL) -- navigate, verify heading and button visible
- **test_add_single_element** (smoke, CRITICAL) -- click add, verify 1 delete button
- **test_add_multiple_elements** (regression, NORMAL) -- parametrized with counts 2, 5 -- click add N times, verify N delete buttons
- **test_remove_single_element** (regression, CRITICAL) -- add 1, delete it, verify 0 remain
- **test_remove_all_elements** (regression, NORMAL) -- add 3, delete all, verify 0 remain
- **test_add_element_after_removing** (regression, NORMAL) -- add 2, remove 1, add 1 more, verify 2 remain

All tests follow AAA pattern, receive page via fixture, use `expect()` for DOM assertions via POM verify methods.
