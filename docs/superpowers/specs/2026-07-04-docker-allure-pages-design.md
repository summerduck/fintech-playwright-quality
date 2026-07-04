# Design: Dockerized Test Runner + Allure on GitHub Pages

**Date:** 2026-07-04
**Status:** Approved
**Roadmap phase:** Docker + CI (README: "Dockerized test runner, CI matrix, Allure on GitHub Pages")

## Goal

Make the E2E suite fully reproducible with one command (`docker compose run --rm tests`),
run it in CI across three browsers, and publish a single Allure report with trend history
to GitHub Pages on every push to `main`.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Docker boundary | Compose with two services: `app` (Stripe sample) + `tests` (runner) | Local run == CI run; removes ~40 lines of app-boot YAML from the workflow |
| Runner base image | `mcr.microsoft.com/playwright/python:v1.58.0-noble` | Matches `playwright==1.58.0` pin; all three browsers preinstalled; industry standard |
| CI matrix | `browser: [chromium, firefox, webkit]`, all blocking | Cross-browser coverage is real E2E value; a red webkit fails the PR |
| Allure publishing | Single merged report, `main` only, history via `gh-pages` branch (`peaceiris/actions-gh-pages`) | One trend line across runs; branch-based deploy lets us fetch previous history |
| Browser identity in report | `browser` added as an Allure parameter in `conftest.py` | Without it, identical test names from 3 browsers collapse into "retries" |

## New Files

### `docker/app.Dockerfile`
- Base: `python:3.12-slim`.
- `git clone --depth 1 https://github.com/stripe-samples/accept-a-payment.git` at build time.
- Install `custom-payment-flow/server/python/requirements.txt`.
- Env: `FLASK_APP=server.py`, `STATIC_DIR=../../client/html`.
- `CMD`: `flask run --host 0.0.0.0 --port 4242`.
- `HEALTHCHECK`: curl `http://localhost:4242/card.html`.
- Stripe keys are **runtime-only** env vars (`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`) — never baked into the image.

### `docker/runner.Dockerfile`
- Base: `mcr.microsoft.com/playwright/python:v1.58.0-noble`.
- Copy `requirements.txt`, `pip install`, then copy the test code.
- Image tag must stay in sync with the `playwright==` pin in `requirements.txt`
  (anchor comments in both files: "keep in sync").

### `docker-compose.yml`
- Service `app`: build from `docker/app.Dockerfile`, port 4242, healthcheck,
  Stripe keys passed through from the host environment.
- Service `tests`: build from `docker/runner.Dockerfile`,
  `depends_on: app: condition: service_healthy`, `TEST_ENV=docker`,
  volume mounts for `./allure-results`, `./test-results`, `./test-logs`
  so artifacts land on the host.
- Entrypoint `pytest tests/framework tests/accept_a_payment`; extra args
  (e.g. `--browser=firefox`) pass through `docker compose run --rm tests <args>`.

## Changes to Existing Files

| File | Change |
|------|--------|
| `config/__init__.py` | Add `"docker"` to `VALID_ENVS`; add `"docker": "http://app:4242"` to `APP_URLS["acceptapayment"]` |
| `pyproject.toml` | Fix inverted naming: `--alluredir=allure-report` → `--alluredir=allure-results` |
| `Taskfile.yml` | Fix `allure generate` args (results in `allure-results/`, report to `allure-report/`); add `docker-build` and `docker-test` tasks; update `clean`/`clean-all` for the corrected dirs |
| `conftest.py` | Add `browser` as an Allure parameter per test so merged multi-browser results render as parameterized runs |
| `.github/workflows/tests.yml` | Rewrite: matrix over browsers, compose-based run, delete manual app-boot steps, add `publish-report` job |
| `.gitignore` | Ensure `allure-results/` is ignored |
| `README.md` | Docker quick start, Pages report link, roadmap phase → Done |

## CI Flow (`tests.yml`)

### Job `tests` (matrix: chromium, firefox, webkit)
1. Checkout.
2. Verify Stripe secrets (keep existing fail-fast step, unchanged message).
3. `docker compose build` with GitHub Actions layer cache.
4. `docker compose run --rm tests --browser=${{ matrix.browser }}`.
5. On failure: `docker compose logs app` (replaces `cat app-server.log`).
6. Always: upload artifact `allure-results-${{ matrix.browser }}` plus traces/logs,
   `if-no-files-found: ignore`, retention 14 days.

### Job `publish-report`
- `needs: tests`, `if: github.ref == 'refs/heads/main' && always()` —
  a red run still publishes (failed runs in the trend are more honest than a stale green report).
- Steps:
  1. Download all `allure-results-*` artifacts into one `allure-results/` directory.
  2. Checkout `gh-pages` (if it exists) and copy `last-history` into `allure-results/history/` —
     guarded so the first-ever run proceeds without history.
  3. `allure generate allure-results -o allure-report --clean`.
  4. Deploy with `peaceiris/actions-gh-pages` to the `gh-pages` branch.
- Report URL: `https://summerduck.github.io/fintech-playwright-quality/`.

### One-time manual setup
Repository Settings → Pages → "Deploy from branch: gh-pages". Documented in README.

## Error Handling

- **App fails to boot** → healthcheck never passes, `docker compose run` exits non-zero
  before tests start; `docker compose logs app` dumped on failure.
- **Missing Stripe keys** → existing fail-fast step blocks before any build.
- **Partial/empty allure results** (a matrix job died) → `allure generate` tolerates
  partial input; artifact upload uses `if-no-files-found: ignore`.
- **No `gh-pages` branch yet** (first run) → history step is guarded; report generates
  without trends, trends appear from the second run.
- **Playwright version drift** → anchor comments in `requirements.txt` and
  `docker/runner.Dockerfile`; a mismatch fails loudly at runner startup.

## Non-Goals

- No PR-preview reports (main-only publishing).
- No Python-version matrix.
- No change to the local non-Docker workflow (`TEST_ENV=local` keeps working as-is).

## Acceptance Criteria

1. `docker compose run --rm tests` locally passes the full suite with no manually started app.
2. CI shows three green browser jobs on a PR; manual app-boot YAML is gone.
3. After merge to `main`, the Allure report is live on GitHub Pages; from the second
   run onward, trend charts render and browsers appear as test parameters.
4. README updated: Docker quick start, report link, roadmap phase marked Done.
