# Test Automation Lifecycle

## Stages & Responsibilities

| # | Stage | Engineer | AI |
|---|-------|-------|----|
| 0 | Requirements Review | writes the requirement, answers clarifying questions | checks testability, flags ambiguities, asks questions |
| 1 | Explore Codebase | — | reads files, maps structure, finds reusable patterns |
| 2 | Design | approves or rejects page object + test case design | proposes locators, methods, test scenarios |
| 3 | Implement | approves plan before code is written | writes page object, fixtures, test file |
| 4 | Run & Debug | — | runs tests, reads output, traces root cause, fixes |
| 5 | Review | final approval | checks POM/AAA/FIRST compliance, flags issues |
| 6 | Commit & PR | approves commit message and PR description | stages files, writes message, opens PR |
| 7 | CI Execution | monitors pipeline | reads CI output, diagnoses env-specific failures |
| 8 | Reporting | reads report, decides next action | parses output, summarizes pass/fail/flaky/gaps |
| 9 | Maintenance | describes what changed in the app | traces broken tests, updates selectors/methods |
| 10 | Optimization | decides what to keep or drop | detects flaky/slow tests, flags redundant coverage |

## Key Pattern

- **Engineer owns:** intent (requirements, approvals, decisions)
- **AI owns:** execution (reading, writing, running, analyzing)
- **Shared:** design (AI proposes, Engineer approves) and review (AI checks, Engineer decides)

## Commands & Agents Map

| # | Stage | Command | Agent(s) | Status |
|---|-------|---------|----------|--------|
| 0 | Requirements Review | `/requirements_review` | `requirements-reviewer` | ✅ built |
| 1 | Explore Codebase | `/explore_codebase` | `codebase-explorer` | ✅ built |
| 2 | Design | `/design_tests` | `design`, `plan`, `codebase-explorer` | ✅ built |
| 3 | Implement | `/implement_tests` | `plan`, `implement`, `review`, `test-runner` | ✅ built |
| — | Orchestration | (removed — commands chain manually) | ~~`lead`~~ | ❌ removed |
| 4 | Run & Debug | `/run_and_debug` | `bug-tracer`, `implement` | ✅ built |
| 5 | Review | (part of `/implement_tests`) | `review` | ✅ built |
| 6 | Commit & PR | `/commit` | — | ✅ built-in |
| 7 | CI Execution | — | — | manual |
| 8 | Reporting | `/reporting` | `reporter` | ✅ built |
| 9 | Maintenance | `/maintenance` | `codebase-explorer`, `maintainer` | ✅ built |
| 10 | Optimization | `/optimization` | `optimizer`, `maintainer` | ✅ built |

## Output Directories

| Stage | Output |
|-------|--------|
| 0 | `thoughts/requirements/` |
| 1 | `thoughts/research/` |
| 2 | `thoughts/test-designs/` |
| 3 | `.claude/agents/plan.md` + code files |
| 4 | `thoughts/debug/` |
| 8 | `thoughts/reports/` |
| 9 | `thoughts/maintenance/` |
| 10 | `thoughts/optimization/` |
