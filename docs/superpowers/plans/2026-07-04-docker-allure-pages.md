# Docker Test Runner + Allure on GitHub Pages — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the full E2E suite with one command (`docker compose run --rm tests`), across a 3-browser CI matrix, and publish a single Allure report with trend history to GitHub Pages on every push to `main`.

**Architecture:** Two-service docker-compose: `app` (Stripe accept-a-payment sample, cloned at image build, healthchecked) and `tests` (official Playwright Python image, `pytest` entrypoint). CI builds both images with GHA layer cache, runs the suite once per browser, then an aggregate job merges the three `allure-results` sets, grafts history from the `gh-pages` branch, and deploys.

**Tech Stack:** Docker Compose, `mcr.microsoft.com/playwright/python:v1.58.0-noble`, GitHub Actions (`docker/bake-action`, `simple-elf/allure-report-action`, `peaceiris/actions-gh-pages`), allure-pytest.

**Spec:** `docs/superpowers/specs/2026-07-04-docker-allure-pages-design.md`

## Global Constraints

- Playwright pin is `playwright==1.58.0` (requirements.txt); the runner base image tag MUST be `v1.58.0-noble` — keep in sync, anchor comments in both files.
- App serves on port `4242`; compose-internal hostname is `app` → base URL `http://app:4242`.
- Stripe keys (`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`) are runtime env only — never baked into images, never printed to logs.
- Raw Allure results live in `allure-results/` (gitignored); the generated report in `allure-report/`.
- All work happens on the existing branch `feat/docker-allure-pages`. Direct commits to `main` are blocked by pre-commit.
- Line length 88, ruff + strict mypy must stay green: run `task quality` before each commit that touches Python.
- Local non-Docker workflow (`TEST_ENV=local`, app started manually) must keep working unchanged.

---

### Task 1: Register the `docker` environment in config

**Files:**
- Modify: `config/__init__.py`
- Modify: `conftest.py` (only the `--env` help string)
- Test: `tests/framework/test_config.py`

**Interfaces:**
- Produces: `get_base_url("acceptapayment", "docker") == "http://app:4242"`; `VALID_ENVS == frozenset(("prod", "local", "docker"))`. Task 5's compose file sets `TEST_ENV=docker` and relies on this resolution.

- [ ] **Step 1: Write the failing tests**

In `tests/framework/test_config.py`, replace `test_invalid_env_error_lists_valid_options` (the sorted env list changes) and add a docker-resolution test inside `TestGetBaseUrl`:

```python
    def test_invalid_env_error_lists_valid_options(self) -> None:
        with pytest.raises(ValueError, match="Valid options: docker, local, prod"):
            get_base_url("acceptapayment", "unknown")

    def test_docker_env_resolves_to_compose_service_hostname(self) -> None:
        assert get_base_url("acceptapayment", "docker") == "http://app:4242"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/framework/test_config.py -v`
Expected: 2 FAIL — `test_invalid_env_error_lists_valid_options` (message still says `local, prod`) and `test_docker_env_resolves_to_compose_service_hostname` (`No 'docker' URL configured`). The parametrized combination test still passes.

- [ ] **Step 3: Implement the config change**

In `config/__init__.py` replace lines 3–9 with:

```python
VALID_ENVS = frozenset(("prod", "local", "docker"))

APP_URLS: dict[str, dict[str, str]] = {
    "acceptapayment": {
        "local": "http://localhost:4242",
        # Hostname of the `app` service on the docker-compose network.
        "docker": "http://app:4242",
    },
}
```

In `conftest.py`, update the `--env` option help string:

```python
        help="Target environment: prod | local | docker",
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/framework/test_config.py -v`
Expected: PASS, including a new auto-generated param case `acceptapayment-docker`.

- [ ] **Step 5: Quality gate and commit**

```bash
task quality
git add config/__init__.py conftest.py tests/framework/test_config.py
git commit -m "feat(config): add docker environment resolving to compose hostname"
```

---

### Task 2: Fix inverted `allure-results` / `allure-report` naming

**Files:**
- Modify: `pyproject.toml` (addopts)
- Modify: `Taskfile.yml` (`allure-report`, `allure-serve`, `clean-all` tasks)
- Modify: `.gitignore`

**Interfaces:**
- Produces: raw results in `allure-results/` (Tasks 5 and 6 mount/upload this exact path); generated report in `allure-report/`.

- [ ] **Step 1: Fix pyproject addopts**

In `pyproject.toml`, in `[tool.pytest.ini_options] addopts`, change:

```toml
    "--alluredir=allure-results",
```

(was `--alluredir=allure-report`).

- [ ] **Step 2: Fix Taskfile allure tasks**

In `Taskfile.yml`, replace the bodies of `allure-report` and `allure-serve`:

```yaml
  allure-report:
    desc: Generate Allure report from raw results
    cmds:
      - echo "Generating Allure report..."
      - allure generate allure-results -o allure-report --clean
      - echo "Allure report generated in allure-report/"

  allure-serve:
    desc: Generate and serve Allure report
    cmds:
      - echo "Generating and serving Allure report..."
      - allure serve allure-results
```

`clean-all` already removes both `allure-report/` and `allure-results/` — no change needed there.

- [ ] **Step 3: Ignore the raw results directory**

In `.gitignore`, in the `# Test logs` block, add `allure-results/` next to the existing `allure-report/` line:

```gitignore
# Test logs
test-logs/
allure-report/
allure-results/
report.html
htmlcov/
mutants/
```

- [ ] **Step 4: Verify results land in the new directory**

```bash
rm -rf allure-results allure-report
pytest tests/framework -q
ls allure-results/ | head -3
git status --short
```

Expected: `allure-results/` contains `*-result.json` files; `git status` does NOT list `allure-results/`.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml Taskfile.yml .gitignore
git commit -m "fix(allure): raw results in allure-results/, report in allure-report/"
```

---

### Task 3: Add `browser` as an Allure parameter

**Files:**
- Modify: `conftest.py`
- Test: manual verification via generated result JSON (fixture wiring, not unit-testable business logic)

**Interfaces:**
- Consumes: `browser_name: str` session fixture from pytest-playwright.
- Produces: every test's Allure result carries parameter `browser`; Task 6's merged report renders 3 browsers as parameterized runs instead of collapsing them into retries.

- [ ] **Step 1: Add the autouse fixture**

In `conftest.py`, add `import allure` to the imports (after `import pytest`), and add under the "Shared Fixtures" section:

```python
@pytest.fixture(autouse=True)
def _allure_browser_parameter(browser_name: str) -> None:
    """Attach the browser name as an Allure parameter to every test.

    Without it, identical test names from different browsers collapse
    into "retries" when multi-browser results are merged into one report.
    """
    allure.dynamic.parameter("browser", browser_name)
```

- [ ] **Step 2: Verify the parameter appears in results**

```bash
rm -rf allure-results
pytest tests/framework/test_config.py -q
grep -l '"name": "browser"' allure-results/*-result.json | head -1
```

Expected: at least one file path printed (parameter present in result JSON).

- [ ] **Step 3: Quality gate and commit**

```bash
task quality
git add conftest.py
git commit -m "feat(allure): record browser as test parameter for merged reports"
```

---

### Task 4: App-under-test Docker image

**Files:**
- Create: `docker/app.Dockerfile`

**Interfaces:**
- Produces: image serving `http://localhost:4242/card.html` with a Docker healthcheck; Task 5's compose `depends_on: service_healthy` relies on that healthcheck. Requires `STRIPE_SECRET_KEY` / `STRIPE_PUBLISHABLE_KEY` at runtime.

- [ ] **Step 1: Write the Dockerfile**

Create `docker/app.Dockerfile`:

```dockerfile
# App under test: stripe-samples/accept-a-payment (custom-payment-flow, Python server).
# Stripe keys are runtime-only env vars — never bake them into the image.
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/stripe-samples/accept-a-payment.git /app

WORKDIR /app/custom-payment-flow/server/python
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=server.py
# server.py resolves STATIC_DIR relative to its own file; ../../client/html serves card.html.
ENV STATIC_DIR=../../client/html

EXPOSE 4242

HEALTHCHECK --interval=2s --timeout=5s --retries=30 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:4242/card.html')"

CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0", "--port", "4242"]
```

- [ ] **Step 2: Build and smoke-test the image**

Stripe test keys must be present in the project `.env` (they already are for local runs).

```bash
docker build -f docker/app.Dockerfile -t fintech-app:local docker/
docker run -d --rm --name fintech-app-smoke --env-file .env -p 4242:4242 fintech-app:local
sleep 5
curl -sSf http://localhost:4242/card.html > /dev/null && echo "APP OK"
docker inspect --format '{{.State.Health.Status}}' fintech-app-smoke
docker stop fintech-app-smoke
```

Expected: `APP OK`, health status `healthy`.

- [ ] **Step 3: Commit**

```bash
git add docker/app.Dockerfile
git commit -m "feat(docker): app-under-test image with healthcheck on /card.html"
```

---

### Task 5: Runner image, docker-compose, Taskfile tasks

**Files:**
- Create: `docker/runner.Dockerfile`
- Create: `docker-compose.yml`
- Create: `.dockerignore`
- Modify: `Taskfile.yml` (add `docker-build`, `docker-test`)
- Modify: `requirements.txt` (anchor comment only)

**Interfaces:**
- Consumes: `fintech-app:local` healthcheck (Task 4), `TEST_ENV=docker` resolution (Task 1), `allure-results/` output path (Task 2).
- Produces: `docker compose run --rm tests [pytest args]` runs the suite; images named `fintech-app:local` / `fintech-tests:local` (Task 6's bake step builds these exact tags). Artifacts appear on the host in `./allure-results`, `./test-results`, `./test-logs`.

- [ ] **Step 1: Write the runner Dockerfile**

Create `docker/runner.Dockerfile`:

```dockerfile
# Base image version MUST match the playwright== pin in requirements.txt.
FROM mcr.microsoft.com/playwright/python:v1.58.0-noble

WORKDIR /work

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Args passed to `docker compose run tests <args>` land directly on pytest.
ENTRYPOINT ["pytest"]
```

Add the matching anchor comment in `requirements.txt` on the playwright line:

```text
playwright==1.58.0  # keep in sync with docker/runner.Dockerfile base image tag
```

- [ ] **Step 2: Write .dockerignore**

Create `.dockerignore` (keeps the build context small and test artifacts out of the image):

```text
.git
.venv
venv
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
.claude
allure-report
allure-results
test-results
test-logs
report.html
docs
.notes
```

- [ ] **Step 3: Write docker-compose.yml**

Create `docker-compose.yml` at the repo root:

```yaml
services:
  app:
    build:
      context: docker
      dockerfile: app.Dockerfile
    image: fintech-app:local
    ports:
      - "4242:4242"
    environment:
      # Read from the host environment or the project .env file.
      STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY}
      STRIPE_PUBLISHABLE_KEY: ${STRIPE_PUBLISHABLE_KEY}

  tests:
    build:
      context: .
      dockerfile: docker/runner.Dockerfile
    image: fintech-tests:local
    depends_on:
      app:
        condition: service_healthy
    environment:
      TEST_ENV: docker
    volumes:
      - ./allure-results:/work/allure-results
      - ./test-results:/work/test-results
      - ./test-logs:/work/test-logs
```

- [ ] **Step 4: Add Taskfile tasks**

In `Taskfile.yml`, add a new section after the Testing section:

```yaml
  # ============================================================================
  # Docker
  # ============================================================================

  docker-build:
    desc: Build app and test runner Docker images
    cmds:
      - docker compose build

  docker-test:
    desc: "Run the suite in Docker (usage: task docker-test -- --browser=firefox)"
    cmds:
      - defer: docker compose down
      - docker compose run --rm tests {{.CLI_ARGS}}
```

- [ ] **Step 5: Run the full suite in Docker**

```bash
task docker-build
rm -rf allure-results test-results test-logs
docker compose run --rm tests
docker compose down
ls allure-results/ | head -3
```

Expected: all tests pass inside the container (app boots via healthcheck, no manual start); `allure-results/` populated on the host.

- [ ] **Step 6: Cross-browser spot check**

```bash
docker compose run --rm tests --browser=firefox tests/accept_a_payment -q
docker compose down
```

Expected: suite passes on firefox.

- [ ] **Step 7: Commit**

```bash
git add docker/runner.Dockerfile docker-compose.yml .dockerignore Taskfile.yml requirements.txt
git commit -m "feat(docker): compose stack — app + playwright runner, task docker-test"
```

---

### Task 6: Rewrite CI workflow — browser matrix + Allure publish

**Files:**
- Modify: `.github/workflows/tests.yml` (full rewrite)

**Interfaces:**
- Consumes: compose services and image tags from Task 5; `allure-results/` host path from Task 2.
- Produces: artifacts `allure-results-{chromium,firefox,webkit}`; `gh-pages` branch with the published report at `https://summerduck.github.io/fintech-playwright-quality/`.

- [ ] **Step 1: Replace tests.yml entirely**

```yaml
name: Tests

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

concurrency:
  group: tests-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: write

jobs:
  tests:
    name: e2e (${{ matrix.browser }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        browser: [chromium, firefox, webkit]
    env:
      STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
      STRIPE_PUBLISHABLE_KEY: ${{ secrets.STRIPE_PUBLISHABLE_KEY }}

    steps:
      - name: Checkout
        uses: actions/checkout@v6

      # Fail early with an actionable message instead of letting every
      # payment test fail cryptically when the app boots without keys.
      - name: Verify Stripe test keys are configured
        run: |
          if [ -z "$STRIPE_SECRET_KEY" ] || [ -z "$STRIPE_PUBLISHABLE_KEY" ]; then
            echo "::error::STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY repo secrets are required. Add them under Settings -> Secrets and variables -> Actions (use Stripe TEST-mode keys)."
            exit 1
          fi

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build images (GHA layer cache)
        uses: docker/bake-action@v6
        with:
          files: docker-compose.yml
          load: true
          set: |
            *.cache-from=type=gha
            *.cache-to=type=gha,mode=max

      - name: Run tests (${{ matrix.browser }})
        run: docker compose run --rm tests --browser=${{ matrix.browser }}

      - name: Dump app logs on failure
        if: failure()
        run: docker compose logs app

      - name: Shut down compose stack
        if: always()
        run: docker compose down -v

      - name: Upload Allure results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: allure-results-${{ matrix.browser }}
          path: allure-results/
          if-no-files-found: ignore
          retention-days: 14

      - name: Upload traces and logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-artifacts-${{ matrix.browser }}
          path: |
            test-results/
            test-logs/
          if-no-files-found: ignore
          retention-days: 14

  publish-report:
    name: Publish Allure report to GitHub Pages
    runs-on: ubuntu-latest
    needs: tests
    # Publish from main even when tests are red: failed runs in the trend
    # are more honest than a stale green report.
    if: always() && github.ref == 'refs/heads/main'

    steps:
      - name: Download Allure results from all browsers
        uses: actions/download-artifact@v4
        with:
          pattern: allure-results-*
          merge-multiple: true
          path: allure-results

      - name: Fetch gh-pages history
        uses: actions/checkout@v6
        # First run: gh-pages does not exist yet — report generates without trends.
        continue-on-error: true
        with:
          ref: gh-pages
          path: gh-pages

      - name: Generate report with history
        uses: simple-elf/allure-report-action@v1.12
        with:
          allure_results: allure-results
          gh_pages: gh-pages
          allure_report: allure-report
          allure_history: allure-history
          keep_reports: 20

      - name: Deploy to gh-pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_branch: gh-pages
          publish_dir: allure-history
```

Notes for the implementer:
- `report.html` (pytest-html) is intentionally no longer uploaded — Allure is the canonical CI report; pytest-html remains a local convenience.
- The old app-boot steps (clone/install/start/wait, ~40 lines) are gone on purpose: the compose healthcheck + `depends_on` replace them.
- Top-level `permissions: contents: write` is required for the gh-pages push with `GITHUB_TOKEN`.

- [ ] **Step 2: Validate workflow syntax**

Run: `actionlint .github/workflows/tests.yml` if actionlint is installed; otherwise `python -c "import yaml, sys; yaml.safe_load(open('.github/workflows/tests.yml'))" && echo YAML_OK`.
Expected: no errors / `YAML_OK`.

- [ ] **Step 3: Commit and push to trigger CI**

```bash
git add .github/workflows/tests.yml
git commit -m "ci: browser matrix in compose + Allure publish to GitHub Pages"
git push -u origin feat/docker-allure-pages
```

- [ ] **Step 4: Open a PR and watch the matrix**

```bash
gh pr create --base main --title "Docker test runner + browser matrix + Allure on GitHub Pages" --fill
gh pr checks --watch
```

Expected: three `e2e (browser)` checks green. `publish-report` is skipped on the PR (main-only) — that is correct behavior.

---

### Task 7: README, roadmap, one-time Pages setup

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: `task docker-test` (Task 5), report URL (Task 6).

- [ ] **Step 1: Update Quick Start**

In `README.md`, after the existing Quick Start commands block, add:

````markdown
### Docker (no local setup needed)

```bash
# Stripe TEST-mode keys in .env: STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
task docker-test                          # full suite, chromium
task docker-test -- --browser=firefox     # any Playwright browser
```

The compose stack boots the app under test and the Playwright runner;
artifacts land in `allure-results/`, `test-results/`, `test-logs/`.
````

- [ ] **Step 2: Update the Stack table, roadmap and add the report link**

- In the Stack table, `Infrastructure` row: replace `_planned_ — Docker` with `Docker Compose`.
- In the Roadmap table, change the `Docker + CI` row status from `⏳ In Progress` to `✅ Done`.
- Under the badges/intro, add the report link line:

```markdown
📊 **Live Allure report:** https://summerduck.github.io/fintech-playwright-quality/ (updated on every push to `main`, with cross-run trend history)
```

- [ ] **Step 3: Document the one-time Pages switch**

Add to the README (near the report link or in a footnote):

```markdown
> One-time repo setup for the report: Settings → Pages → Deploy from branch → `gh-pages` / root.
```

The repo owner must flip this setting manually after the first `publish-report` run creates the `gh-pages` branch.

- [ ] **Step 4: Commit and push**

```bash
git add README.md
git commit -m "docs: Docker quick start, live Allure report link, roadmap phase done"
git push
```

- [ ] **Step 5: Post-merge verification (after PR approval and merge)**

1. Merge the PR; wait for the `Tests` workflow on `main`.
2. Confirm the `gh-pages` branch exists, flip Settings → Pages to `gh-pages`.
3. Open `https://summerduck.github.io/fintech-playwright-quality/` — report loads, tests show a `browser` parameter.
4. After a second push to `main`, confirm trend charts render.
