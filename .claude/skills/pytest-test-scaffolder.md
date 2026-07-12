---
description: Scaffold pytest test files following project conventions
---

# Pytest Test Scaffolder

Generate test files that match the project's exact conventions.

## Why Use This Test Structure?

### Benefits

✅ **Fixture-Based Page Objects**: Tests receive ready-to-use page instances — no manual instantiation
✅ **Consistent AAA Pattern**: Every test follows Arrange/Act/Assert for readability
✅ **Rich Allure Reports**: Epics, features, stories, and severity on every test
✅ **Data-Driven**: Parametrized tests with `pytest.param(id=)` for clear test IDs
✅ **App Isolation**: Each app directory owns its `base_url` and fixtures
✅ **Strict Markers**: `--strict-markers` prevents typos from silently creating new markers

### Problems It Solves

❌ **Flaky Setup/Teardown**: Manual setup methods replaced by composable fixtures
❌ **Hard-Coded Data**: Raw strings in tests replaced by frozen dataclasses from `config.data`
❌ **Missing Metadata**: Tests without Allure annotations produce empty, unnavigable reports
❌ **Tight Coupling**: Tests that instantiate page objects directly break when constructors change
❌ **Inconsistent Structure**: Ad-hoc test organization makes reviews and onboarding slower

This skill complements:
- **playwright-page-object-generator** — page object classes that tests consume via fixtures
- **allure-report-enhancer** — Allure annotation conventions and report hierarchy

## Before Generating

1. Identify the target app: `acceptapayment`
2. Check which Page Objects exist in `pages/<app>/`
3. Review existing tests in `tests/<app>/` for patterns already in use
4. Read `conftest.py` to confirm available fixtures and hooks

## File Placement

```
tests/
├── accept_a_payment/
│   ├── conftest.py              # Page object fixtures for accept_a_payment
│   └── test_card.py
└── framework/
    └── test_log_helpers.py
```

File naming: `test_<feature>.py` (configured in `pyproject.toml`: `python_files = "test_*.py"`).
Each app directory has a `conftest.py` that provides page object fixtures.

## Conventions

| Aspect | Convention |
|--------|-----------|
| File naming | `test_<feature>.py` — one file per feature or page area |
| Class naming | `Test<Feature>` — groups related scenarios |
| Test naming | `test_<scenario>` — descriptive, uses underscores |
| Page objects | Received as **fixture parameters** from `tests/<app>/conftest.py`, never instantiated |
| Test data | Frozen dataclasses from `config.data.*`, never hard-coded strings |
| Markers | Exactly one app marker + at least one category marker per test |
| Allure | `@allure.epic` + `@allure.feature` on class; `@allure.story` + `@allure.severity` + title on method |
| Assertions | Prefer `expect()` for DOM elements; `assert` only for non-DOM values |
| Type hints | Full annotations on all parameters and return types |
| Logging | Module-level `logger = logging.getLogger(__name__)`; log complex test setup |
| Docstrings | Google-style on every test class and test method |

## Available Markers (from pyproject.toml)

Every test **must** have an app marker plus at least one category marker.

**App markers** (exactly one per test):
- `@pytest.mark.acceptapayment` — tests in `tests/accept_a_payment/`

**Category markers** (one or more):
- `smoke` — quick smoke tests (used in PR fast-feedback workflow)
- `regression` — full regression tests
- `acceptance` — acceptance / end-to-end flows
- `validation` — form and input validation
- `ui_ux` — UI/UX tests
- `security` — security tests
- `accessibility` — accessibility tests
- `network` — network monitoring tests
- `account_creation` — account creation tests
- `slow` — slow running tests
- `performance` — performance tests
- `integration` — integration tests
- `property` — property-based tests (Hypothesis)
- `unit` — unit tests for framework code (no app marker needed)

Note: `--strict-markers` is enabled in `pyproject.toml` addopts. Misspelled markers will fail the test run.

## Available Fixtures

### Root-level fixtures (from root `conftest.py`)

| Fixture | Scope | What it provides | Source |
|---------|-------|------------------|--------|
| `page` | function | Playwright `Page` instance | pytest-playwright plugin |
| `base_url` | function | Base URL for the app under test | `tests/<app>/conftest.py` |
| `user_password` | function | Password from `--user-pw` CLI or `USER_PASSWORD` env var | root `conftest.py` |
| `browser_context_args` | session | Viewport 1280x720, locale `en-GB`, timezone `Europe/London` | root `conftest.py` |

### App-level fixtures (from `tests/<app>/conftest.py`)

Each app directory has its own `conftest.py` that provides **page object fixtures**. Tests never instantiate page objects directly — they receive them as fixture parameters.

| Fixture | Returns | Source |
|---------|---------|--------|
| `card_page` | `CardPage(page, base_url)` | `tests/accept_a_payment/conftest.py` |

Note: page objects are always received as **fixtures**. Methods that transition the user to another page still return `Self` — the next page object comes from a separate fixture parameter, not from the return value of a POM method.

Components are **not** fixtures. A component (e.g. `ThreeDSFrame`, the 3DS iframe on `card.html`) is constructed by the page that owns it and reached through that page's methods — `three_ds_frame.handle_three_ds(...)`, never a `three_ds_frame` fixture. If a thing cannot be navigated to on its own, it does not get a fixture.

### How `base_url` Works

Each app directory defines its own `base_url` fixture in `tests/<app>/conftest.py`:

```python
@pytest.fixture
def base_url() -> str:
    return "http://localhost:4242"
```

This overrides Playwright's built-in `base_url` fixture at directory scope. No global enum or marker introspection needed — each app directory owns its URL. The `--base-url` CLI option still works as a manual override.

## App-Level Conftest Template

Each app directory has a `conftest.py` that provides the `base_url` fixture and page object fixtures. Every page object gets its own fixture:

```python
"""Pytest fixtures for <App> tests.

Provides the base URL and page object fixtures so tests receive
ready-to-use page instances without instantiating them directly.
"""

import pytest
from playwright.sync_api import Page

from pages.<app>.login_page import LoginPage
from pages.<app>.inventory_page import InventoryPage


@pytest.fixture
def base_url() -> str:
    """Base URL for the <App> application."""
    return "<app-base-url>"


@pytest.fixture
def login_page(page: Page, base_url: str) -> LoginPage:
    """Provide a LoginPage instance for the current test."""
    return LoginPage(page, base_url)


@pytest.fixture
def inventory_page(page: Page, base_url: str) -> InventoryPage:
    """Provide an InventoryPage instance for the current test."""
    return InventoryPage(page, base_url)
```

Each app directory owns its `base_url` and page object fixtures. Tests never instantiate page objects directly.

## Automatic Behaviours (from pyproject.toml addopts)

These run automatically — do not duplicate in test code or commands:
- `--reruns=1` — failed tests are retried once
- `--cov=pages --cov=utils --cov=config` — coverage collected on page objects and utilities
- `--alluredir=allure-results` — Allure results directory
- `--html=report.html` — HTML report generated
- `-v --tb=short` — verbose output, short tracebacks
- `--strict-markers` — undefined markers cause errors

## Test Data Models

Tests **must not** contain hardcoded credentials or form data. Use the frozen dataclasses from `config/data/`:

```
config/data/
└── models.py         # User, Product, CheckoutInfo, CreditCard
```

Page object methods accept the dataclass, not raw strings. All POM methods return `Self`:

```python
# Page object signatures
def login_as(self, user: User) -> Self: ...
```

## Test File Template

Tests receive page objects as **fixture parameters** (defined in the app-level `conftest.py`). Tests never instantiate page objects directly.

```python
"""Tests for <Feature> on <App>."""

import logging

import allure
import pytest
from playwright.sync_api import expect  # import Page only if used directly in this test file

from pages.<app>.<page_name>_page import <PageName>Page

logger = logging.getLogger(__name__)


@allure.epic("<App Name>")
@allure.feature("<Feature Area>")
class Test<Feature>:
    """<Feature> test suite for <App>."""

    @allure.story("<User Story>")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("<Human-readable test title>")
    @pytest.mark.<app>
    @pytest.mark.smoke
    def test_<scenario>(self, <page_name>_page: <PageName>Page) -> None:
        """<What this test verifies>."""
        <page_name>_page.navigate()
        <page_name>_page.some_action()
        <page_name>_page.verify_result()
```

Prefer verification methods on the page object (`verify_page_loaded`, `get_error_message`) over raw `page`/`expect()` in tests.

## Parametrized Test Template

```python
    @allure.story("Dynamic loading examples")
    @pytest.mark.acceptapayment
    @pytest.mark.regression
    @pytest.mark.parametrize(
        ("example", "expected_text"),
        [
            pytest.param(1, "Hello World!", id="example-1"),
            pytest.param(2, "Hello World!", id="example-2"),
        ],
    )
    def test_dynamic_loading(
        self,
        dynamic_loading_page: DynamicLoadingPage,
        example: int,
        expected_text: str,
    ) -> None:
        """Verify text appears after dynamic loading completes."""
        allure.dynamic.title(f"Example {example} shows '{expected_text}' after load")
        allure.dynamic.severity(allure.severity_level.CRITICAL)
        dynamic_loading_page.navigate_to_example(example)
        dynamic_loading_page.click_start()
        dynamic_loading_page.verify_loaded_text(expected_text)
```

## Standalone Function Template

For simpler test files that do not need a class:

```python
"""Tests for <feature> on <App>."""

import logging

import allure
import pytest

from pages.<app>.<page_name>_page import <PageName>Page

logger = logging.getLogger(__name__)


@allure.epic("<App Name>")
@allure.feature("<Feature Area>")
@allure.story("<User Story>")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("<Human-readable test title>")
@pytest.mark.<app>
@pytest.mark.smoke
def test_<scenario>(<page_name>_page: <PageName>Page) -> None:
    """<What this test verifies>."""
    # Arrange
    <page_name>_page.navigate()

    # Act
    <page_name>_page.some_action()

    # Assert
    <page_name>_page.verify_result()
```

## Code Quality

Apply all rules from the **code-quality-standards** skill.

`tests/*` and `conftest.py` have two exemptions (see `pyproject.toml`):
- `ARG` — unused fixture parameters are allowed (fixtures often have side effects)
- `PLR2004` — magic values in assertions are allowed

`assert` is permitted in `test_*.py` via `bandit skips = ["B101"]`; prefer `expect()` for DOM checks.

## Rules

### Do
- One `@allure.epic` per test class — must match the app marker (see allure-report-enhancer skill)
- One `@allure.feature` per test class (maps to the page or feature area)
- One `@allure.story` per test method (maps to the user scenario)
- `@allure.severity` on every test
- `@allure.title` with a human-readable description (or `allure.dynamic.title` for parametrized)
- Always include the app marker **and** at least one category marker
- AAA comments: `# Arrange` / `# Act` / `# Assert`
- Prefer `expect()` from `playwright.sync_api` for auto-waiting assertions on DOM elements
- Use `expect(page).to_have_url()`, `expect(locator).to_have_text()`, `expect(locator).to_be_visible()`
- Use `@pytest.mark.parametrize` when testing 3+ variations of the same scenario
- Always use tuple unpacking: `("param_a", "param_b")`
- Always add `id=` to `pytest.param()` for readable test IDs
- Use `allure.dynamic.title()` inside the test body for parametrized tests

### Do not
- Put **any** Python logic (loops, conditionals, list comprehensions, try/except) in test bodies — tests must consist exclusively of method calls on page objects and fixtures; push all logic into page object or workflow methods
- Use `assert` to check DOM elements — use `expect()` for auto-waiting assertions on DOM
- Instantiate page objects in tests — receive them as fixtures via app-level `conftest.py`
- Put page object logic in tests — keep it in `pages/`
- Use `time.sleep()` — rely on Playwright auto-waiting
- Hard-code URLs — always use `base_url` fixture
- Hard-code credentials, product names, or form data — use `config.data` dataclasses
- Share mutable state between tests
- Use setup/teardown methods — use pytest fixtures instead
- Capture screenshots manually — `conftest.py` handles failure artifacts automatically
- Use `with allure.step()` in tests — steps belong in page object methods via `@allure.step()` decorators
- Import inside test methods — use top-level imports only (except `dataclasses.replace()` for password overrides)

---

### ❌ DON'T

**1. Instantiate Page Objects in Tests**
```python
# Bad: Test creates page objects directly
def test_load(page: Page) -> None:
    dynamic_loading_page = DynamicLoadingPage(page, "http://localhost:4242")
    dynamic_loading_page.navigate()
```

**2. Hard-Code Test Data**
```python
# Bad: Raw strings instead of data models
def test_dynamic_loading(self, dynamic_loading_page: DynamicLoadingPage) -> None:
    dynamic_loading_page.navigate_to_example(1)

# Good: Use parametrize with named IDs for data-driven tests
@pytest.mark.parametrize("example", [pytest.param(1, id="example-1")])
def test_dynamic_loading(self, dynamic_loading_page: DynamicLoadingPage, example: int) -> None:
    dynamic_loading_page.navigate_to_example(example)
```

**3. Use `with allure.step()` in Tests**
```python
# Bad: Manual step blocks in tests
def test_dynamic_loading(self, dynamic_loading_page: DynamicLoadingPage) -> None:
    with allure.step("Navigate"):
        dynamic_loading_page.navigate()
    with allure.step("Click start"):
        dynamic_loading_page.click_start()

# Good: POM methods are already @allure.step() decorated
def test_dynamic_loading(self, dynamic_loading_page: DynamicLoadingPage) -> None:
    dynamic_loading_page.navigate()
    dynamic_loading_page.click_start()
```

**4. Add Assertions in Wrong Layer**
```python
# Bad: Using page internals for assertions
def test_loading(self, dynamic_loading_page: DynamicLoadingPage, page: Page) -> None:
    dynamic_loading_page.navigate()
    dynamic_loading_page.click_start()
    assert page.locator("#finish").is_visible()  # Leaks page structure

# Good: Use page object verification methods
def test_loading(self, dynamic_loading_page: DynamicLoadingPage) -> None:
    dynamic_loading_page.navigate()
    dynamic_loading_page.click_start()
    dynamic_loading_page.verify_element_visible()
```

**5. Missing Markers**
```python
# Bad: No app marker or category marker
@allure.story("Dynamic Loading")
def test_loading(self, dynamic_loading_page: DynamicLoadingPage) -> None:
    ...

# Good: Both app and category markers
@allure.story("Dynamic Loading")
@pytest.mark.acceptapayment
@pytest.mark.smoke
def test_loading(self, dynamic_loading_page: DynamicLoadingPage) -> None:
    ...
```

## Common Anti-Patterns to Avoid

### Anti-Pattern 0: Python Logic in Tests

```python
# Bad: Loop in test body — logic leaks out of the page object layer
def test_add_multiple_elements(self, page: AddRemoveElementsPage) -> None:
    page.navigate()
    for _ in range(5):
        page.click_add_element()
    page.verify_delete_button_count(5)

# Good: Count parameter pushes the loop into the page object
def test_add_multiple_elements(self, page: AddRemoveElementsPage) -> None:
    page.navigate()
    page.click_add_element(5)
    page.verify_delete_button_count(5)
```

**Rule:** Test bodies must be flat sequences of method calls — no `for`, `while`, `if`/`else`, `try`/`except`, list comprehensions, or inline calculations. Push all logic into page objects or workflow methods.

### Anti-Pattern 1: Test Knows Page Structure

```python
# Bad: Test reaches into page internals
def test_item_count(self, page: Page, inventory_page: InventoryPage) -> None:
    inventory_page.navigate()
    items = page.locator(".inventory_item")
    assert items.count() == 6
```

**Solution:** Expose a getter method on the page object (`get_item_count()`).

### Anti-Pattern 2: Shared Mutable State

```python
# Bad: Class-level state shared across tests
class TestCart:
    items_added = []

    def test_add_item(self, cart_page):
        self.items_added.append("Backpack")
        ...

    def test_verify_cart(self, cart_page):
        assert len(self.items_added) == 1  # Depends on test order
```

**Solution:** Each test is fully independent. Use fixtures for shared setup.

### Anti-Pattern 3: Parametrize Without IDs

```python
# Bad: No test IDs — report shows [0], [1], [2]
@pytest.mark.parametrize("example,expected", [
    (1, "Hello World!"),
    (2, "Hello World!"),
])
def test_dynamic_loading(self, dynamic_loading_page, example, expected): ...

# Good: Named test IDs for readable reports
@pytest.mark.parametrize(
    ("example", "expected_text"),
    [
        pytest.param(1, "Hello World!", id="example-1"),
        pytest.param(2, "Hello World!", id="example-2"),
    ],
)
def test_dynamic_loading(self, dynamic_loading_page, example, expected_text): ...
```
