# Test Automation Lifecycle

## Stages & Responsibilities

| # | Stage | Engineer | AI |
|---|-------|-------|----|
| 0 | Requirements Review | writes the requirement, answers clarifying questions | checks testability, flags ambiguities, asks questions |
| 1 | Explore Codebase | triggers exploration, defines scope | reads files, maps structure, finds reusable patterns |
| 2 | Test Plan | approves or rejects scope, scenarios, and priorities | defines what to test: scope, scenarios, risks, coverage goals |
| 3 | Design | approves or rejects page object + test case design | proposes locators, methods, test scenarios |
| 4 | Implement | approves plan before code is written | writes page object, fixtures, test file |
| 5 | Run & Debug | runs tests | reads output, traces root cause, fixes |
| 6 | Review | final approval | checks POM/AAA/FIRST compliance, flags issues |
| 7 | Commit & PR | approves commit message and PR description | stages files, writes message, opens PR |
| 8 | CI Execution | monitors pipeline | reads CI output, diagnoses env-specific failures |
| 9 | Reporting | reads report, decides next action | parses output, summarizes pass/fail/flaky/gaps |
| 10 | Maintenance | describes what changed in the app | traces broken tests, updates selectors/methods |
| 11 | Optimization | decides what to keep or drop | detects flaky/slow tests, flags redundant coverage |

## Key Pattern

- **Engineer owns:** intent (requirements, approvals, decisions)
- **AI owns:** execution (reading, writing, running, analyzing)
- **Shared:** design and review — AI proposes/checks, Engineer approves/decides

## Commands & Agents Map

| # | Stage | Command | Agent(s) | Status |
|---|-------|---------|----------|--------|
| 0 | Requirements Review | `/requirements_review` | `requirements-reviewer` | ✅ built |
| 1 | Explore Codebase | `/explore_codebase` | `codebase-explorer` | ✅ built |
| 2 | Test Plan | `/test_plan` | `test-planner` | ✅ built |
| 3 | Design | `/design_tests` | `design`, `codebase-explorer` | ✅ built |
| 4 | Implement | `/implement_tests` | `plan`, `implement`, `review`, `test-runner` | ✅ built |
| 5 | Debug | `/debug` | `bug-tracer`, `implement` | ✅ built |
| 6 | Review | `/review` | `review` | ✅ built |
| 7 | Commit & PR | `/open_pr` | — | ✅ built |
| 8 | CI Execution | — | — | ⬜ pending MCP |
| 9 | Reporting | `/reporting` | `reporter` | ✅ built |
| 10 | Maintenance | `/maintenance` | `codebase-explorer`, `maintainer` | ✅ built |
| 11 | Optimization | `/optimization` | `optimizer`, `maintainer` | ✅ built |
