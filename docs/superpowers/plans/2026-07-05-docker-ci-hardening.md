# Docker/CI Hardening Batch

Deferred non-blocking findings from the PR #50 final review, closed as one small PR.

## Global Constraints

- A repo hook BLOCKS any Bash command whose text contains the string `.env`. Never run such a command (no `cat .env`, no `grep .env ...`). Use the Read/Edit tools for files instead. `docker compose` reads the project `.env` natively without the string appearing in your command — that is fine. If you genuinely need a blocked command, report BLOCKED.
- Do not commit or echo Stripe keys. Keys live in the project `.env` and are runtime-only.
- KISS/YAGNI per `.claude/CLAUDE.md`. Tests are flat sequences — no loops/conditionals in test bodies.
- One commit per task, conventional message style (`chore: ...`, `ci: ...`, `fix: ...`).
- Do not change CI workflow behavior beyond what the task specifies.

## Task 1: Harden app.Dockerfile (non-root, healthcheck start-period, digest pin)

**File:** `docker/app.Dockerfile`

1. **Pin base image by digest.** Run `docker buildx imagetools inspect python:3.12-slim` and take the top-level manifest-list digest. Change the FROM line to `FROM python:3.12-slim@sha256:<digest>` (keep the tag for readability).
2. **Non-root user.** After the pip install layer, add a system user and switch to it before CMD:
   ```dockerfile
   RUN useradd --system --uid 10001 appuser
   USER appuser
   ```
   The app only reads `/app` (root-owned, world-readable) and writes nothing — no chown needed.
3. **Healthcheck.** Replace the current `--interval=2s --timeout=5s --retries=30` with:
   ```dockerfile
   HEALTHCHECK --interval=5s --timeout=5s --start-period=30s --retries=3 \
   ```
   (CMD line unchanged.) Failures during start-period don't count toward retries.

**Verify:**
- `docker compose build app`
- `docker compose up -d app --wait` (compose reads Stripe keys from the project env file natively — do NOT reference the env file in your command)
- `docker inspect --format '{{.State.Health.Status}}' $(docker compose ps -q app)` → `healthy`
- `docker compose exec app whoami` → `appuser`
- `curl -sf http://localhost:4242/card.html > /dev/null && echo OK`
- `docker compose down`

## Task 2: Config tweaks (.dockerignore, loopback port bind, CI job timeouts)

1. **`.dockerignore`** — append these lines (image-bloat-only; runner build context is repo root):
   ```
   .superpowers
   .hypothesis
   .vscode
   .github
   ```
2. **`docker-compose.yml`** — change the app port mapping from `"4242:4242"` to `"127.0.0.1:4242:4242"`. The CI `tests` service reaches the app over the compose network (service DNS), not the host port, so CI is unaffected; local runs hit localhost anyway.
3. **`.github/workflows/tests.yml`** — add `timeout-minutes: 20` to the `tests` job and `timeout-minutes: 10` to the `publish-report` job (job level, right after `runs-on`).

**Verify:**
- `docker compose config -q` (compose file still valid)
- `python -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('.github/workflows/tests.yml').read_text())"` (workflow parses)

## Task 3: log_helpers — symlink guard + stale allure-results cleanup

**Files:** `utils/log_helpers.py`, new `tests/framework/test_log_helpers.py`

1. In `clean_and_create_log_dirs()`, the clean loop must not `shutil.rmtree` a symlinked directory (rmtree follows the link and destroys the target). Symlinks — dir or file — get `unlink()`.
2. Stale local allure results currently accumulate across runs. Add `ALLURE_RESULTS_DIR = Path("allure-results")` next to `LOG_DIR` and empty its *contents* in `clean_and_create_log_dirs()` too (do not remove the directory itself — it is a bind mount in Docker; recreate it if missing). Extract one private helper, e.g. `_empty_dir_contents(path: Path)`, used for both `LOG_DIR` and `ALLURE_RESULTS_DIR` (DRY).
3. TDD: write `tests/framework/test_log_helpers.py` first (style-match `tests/framework/test_config.py`). Cover at minimum, using `tmp_path` and monkeypatching the module-level dir constants:
   - regular subdirs and files inside `LOG_DIR` are removed
   - a symlinked dir inside `LOG_DIR` is unlinked and its target survives
   - `ALLURE_RESULTS_DIR` contents are emptied but the directory remains
   - missing dirs are created
   Flat test bodies (no loops/conditionals) per project rules.

**Verify:** `python -m pytest tests/framework/test_log_helpers.py -q` and `python -m pytest tests/framework -q`; `ruff check utils tests/framework` and `mypy utils` if configured.
