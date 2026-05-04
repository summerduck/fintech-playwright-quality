# AI-Augmented Fintech Testing Platform

[![Code Quality](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![Python](https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=white)](https://www.python.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.51+-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev)
[![Ruff](https://img.shields.io/badge/linting-Ruff-261230?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Work in progress**

Production-grade test automation platform with integrated AI agents that demonstrating how AI changes quality engineering, not just speeds up test writing.

---

## Stack

| Layer | Technologies |
|-------|-------------|
| **E2E Testing** | Playwright, pytest, pytest-xdist |
| **API Testing** | httpx |
| **AI Layer** | Claude API (claude-sonnet-4-7), multi-agent workflows, LLM-as-Judge |
| **Code Quality** | Ruff, mypy (strict), Bandit, pip-audit, Radon |
| **Infrastructure** | Docker, GitHub Actions, Allure |
| **App Under Test** | stripe-samples/accept-a-payment (payments domain) |

---

## What's Built

- **Code quality infrastructure** — pre-commit hooks, strict mypy, CI enforcement
- **Page Object Model** — reusable abstractions across applications
- **Multi-agent setup** — Claude API + Playwright MCP pipeline
- **CI/CD** — GitHub Actions: code quality + test workflows
- **ADRs** — architectural decisions documented (001–004)

---

## Roadmap

| Phase | Status | Goal |
|-------|--------|------|
| Foundation & Code Quality | ✅ Done | Repo, CI, pre-commit, pyproject |
| AI Setup | ✅ Done | Claude API, multi-agent, Playwright MCP |
| Framework Foundation | ✅ Done | POM patterns, The Internet app |
| Docker + CI | ⏳ In Progress | Dockerized test runner, CI matrix, Allure on GitHub Pages |
| Payments App | Planned | Stripe E2E + API tests (15+ scenarios) |
| AI Integration | Planned | Test Generator, Failure Triage, LLM-as-Judge — all with accuracy metrics |
| Performance Testing | Planned | Locust load scenarios, CI threshold gate |
| Polish | Planned | Architecture diagrams, full walkthrough |

---

## AI Components (Planned)

Three agents targeting the payments test suite — each with measurable accuracy:

**Test Generator** — takes a user story, outputs a pytest + Playwright test scaffold via Claude API.

**Failure Triage Agent** — analyzes failed test name + trace + screenshot, classifies root cause (`real_bug | flaky | env_issue | test_bug`), posts confidence score to PR.

**LLM-as-Judge** — evaluates test quality against a rubric (coverage, assertions, POM usage, naming). Validated against a ground-truth dataset.

---

## Quick Start

```bash
git clone <repo-url>
cd fintech-playwright-quality
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && playwright install chromium
pre-commit install
```

```bash
pytest tests/the_internet/     # Run The Internet tests
pytest -m smoke                # Smoke suite only
task quality                   # Run all quality checks
```

---

## Architecture Decisions

| ADR | Decision |
|-----|----------|
| [ADR-001](docs/arch/ard-001-playwright-selection.md) | Playwright as the E2E framework |
| [ADR-002](docs/arch/ard-002-code-quality-infrastructure.md) | Code quality toolchain |
| [ADR-003](docs/arch/ard-003-pre-commit.md) | Pre-commit over custom git hooks |
| [ADR-004](docs/arch/ard-004-git-strategy.md) | GitHub Flow branching strategy |

---

**Author:** Daria Samardak · MIT License
