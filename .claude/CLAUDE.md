# General Principles

- Never use apologies
- Always verify information before presenting it. Do not make assumptions or speculate without clear evidence.

# Programming Principles

Reference: [Programming Principles Repository](https://github.com/webpro/programming-principles)

## Generic Principles

### KISS (Keep It Simple, Stupid)
Reference: [Principles Wiki — KISS](https://principles-wiki.net/principles:keep_it_simple_stupid)

Most systems work and are understood better if they are kept simple rather than made complex.
- Less code takes less time to write, has less bugs, and is easier to modify
- Simplicity is the ultimate sophistication
- Perfection is reached not when there is nothing left to add, but when there is nothing left to take away
- When reviewing a design, ask: "Can anything be removed without losing functionality?"

### YAGNI (You Aren't Gonna Need It)
Don't implement something until it is necessary.
- Implement things when you actually need them, never when you just foresee that you need them
- Prevents code bloat and unnecessary complexity

### Do The Simplest Thing That Could Possibly Work (DTSTTCPW)
Reference: [C2 Wiki — DTSTTCPW](https://c2.com/xp/DoTheSimplestThingThatCouldPossiblyWork.html)

Real progress against the real problem is maximized if we just work on what the problem really is.
- Two-step process: (1) implement the capability in the simplest straightforward way, (2) refactor the system to be the simplest possible code including all features it now has
- Know at least two ways to do a thing so you can pick the simpler one
- "Could possibly work" — not "will work"; your tests tell you whether it does
- Second-order benefits: done sooner, easier to communicate, duplication is obvious, tests are easier to write, code is easier to performance-tune, less stress
- The cost of recovering from a corner is almost always less than the cost of big up-front design that tries to cover every contingency
- It is far easier to add something to a simple design when needed than to tear apart an extensive design that is not quite right

### Separation of Concerns
Separate a computer program into distinct sections, such that each section addresses a separate concern.
- Business logic and user interface are separate concerns
- Changing one should not require changing the other

### Avoid Premature Optimization
Premature optimization is the root of all evil.
- First make it work, then make it right, then make it fast
- Optimize only when necessary and after profiling

### Keep things DRY (Don't Repeat Yourself)
Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.
- Avoid duplication of logic and data
- Abstract reusable code into functions, classes, or modules

## Code Structure Principles

### Single Responsibility Principle (SRP)
A class should have only one reason to change.
- Every class should have a single responsibility
- That responsibility should be entirely encapsulated by the class
- Each function, class, or module should do one thing well

### Minimize Coupling
Coupling is the degree to which each program module relies on other modules. Lower coupling is better.
- Changes in one module require fewer changes in other modules
- Modules can be understood and reused independently

### Maximize Cohesion
Group related functionalities that form a meaningful unit.
- Reduced module complexity
- Increased maintainability and reusability
- Related code stays together

### Composition Over Inheritance
Favor object composition over class inheritance.
- Composition is more flexible and leads to more maintainable code
- Avoid deep inheritance hierarchies

### SOLID Principles
- **S**ingle Responsibility: A class should have only one reason to change
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Subtypes must be substitutable for their base types
- **I**nterface Segregation: Many specific interfaces are better than one general interface
- **D**ependency Inversion: Depend on abstractions, not concretions

# Testing Principles

### FIRST Principles of Testing
Reference: [Agile in a Flash — F.I.R.S.T](https://agileinaflash.blogspot.com/2009/02/first.html)

- **F**ast — Tests must be fast enough that developers never hesitate to run them. A test taking a second is impossibly slow; tens of thousands of unit tests should run in under a minute. If setup + teardown spans an eighth of a second, that is already slow.
- **I**solated — Each test has a laser-tight focus on a single effect or decision. No order-of-run dependency; tests pass or fail the same way in a suite or individually. Each test imposes its own initial state and cleans up after itself. Test class name + method name + assertion text should state exactly what is wrong and where.
- **R**epeatable — Tests run repeatedly without intervention. They must not depend on assumed initial state or leave residue behind. They do not depend on external services, the network, or a specific server environment.
- **S**elf-validating — Tests are pass/fail with no manual examination of results. Avoid over-specification so peripheral changes don't break assertions.
- **T**imely — Tests are written immediately before the production code that makes them pass. Writing tests post-facto leads to fewer, fatter tests that are slow, poorly isolated, and eventually abandoned.

### Arrange, Act, Assert (AAA Pattern)
Pattern to arrange and format code in tests:
- **Arrange** - Set up all necessary preconditions and inputs
- **Act** - Execute the method or object under test
- **Assert** - Verify that the expected results have occurred


# Python Best Practices

## Code Style
- Follow PEP 8 naming conventions:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
- Maximum line length of 88 characters (Black default)
- Use absolute imports over relative imports

## Type Hints
- Use type hints for function parameters and return types
- Import types from `typing` module (e.g., `Optional`, `List`, `Dict`)
- Use `Optional[Type]` for optional parameters
- Example: `def process_data(name: str, count: Optional[int] = None) -> Dict[str, Any]:`

## Testing with Pytest
- **No Python logic in test bodies** — tests must be flat sequences of method calls on page objects / fixtures / workflows. Loops (`for`, `while`), conditionals (`if`/`else`), try/except, list comprehensions, and inline calculations belong in page object or workflow methods, never in the test itself.
- Use pytest fixtures for setup and teardown
- Follow AAA pattern: Arrange, Act, Assert
- Parametrize tests for multiple scenarios: `@pytest.mark.parametrize`
- Use pytest markers to categorize tests
- Keep tests isolated and independent

## Page Object Model (POM)
- Create page classes that represent web pages
- Encapsulate element locators within page classes
- Methods should represent user actions (e.g., `click_login_button()`)
- Return page objects for method chaining
- Keep locators as class attributes or in separate locator files

## Error Handling
- Use specific exception types rather than bare `except:`
- Handle expected exceptions explicitly
- Log errors with context using Python's `logging` module
- Raise custom exceptions for domain-specific errors
- Use try-except blocks sparingly and only where needed

## Code Organization
- Follow the project's established patterns (Page Object, Workflow, Data Object)
- Keep functions and methods focused on a single responsibility
- Extract reusable logic into utility functions
- Use meaningful variable and function names
- Group related functionality into modules and packages

## Documentation
- Use docstrings for classes and public methods
- Document complex logic with inline comments
- Keep docstrings concise and focused on what/why, not how
- Update documentation when changing functionality

## Best Practices for Test Automation
- Use explicit waits over implicit waits or sleep
- Make tests data-driven where appropriate
- Clean up test data after test execution
- Use context managers for resource management
- Avoid hardcoded values; use configuration or data files
- Handle flaky tests by improving selectors or wait conditions, not by adding retries
