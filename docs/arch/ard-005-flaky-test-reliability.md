# ADR 5: Flaky Test Reliability Policy

## Status

Accepted

## Context

E2E browser tests fail intermittently for reasons unrelated to the code under
test: CI runner load, network noise, browser timing. Untreated, flaky tests
erode trust in the suite — engineers re-run red builds without reading them,
and real regressions slip through. The industry lifecycle for flakes is:
detect → contain → remember → decide → fix.

Alternatives considered: unconditional retries (hides flakes instead of
surfacing them), deleting/skipping flaky tests (loses coverage silently),
external flaky-test services (BuildPulse, Trunk, Datadog — new
infrastructure and cost for a single-repo suite), pytest-quarantine plugin
(abandoned since 2020).

## Decision

Flaky tests are handled by a two-stage, human-in-the-loop policy built from
small custom pytest plugins. Full rationale and thresholds:
`docs/superpowers/specs/2026-07-09-flaky-reliability-v2-design.md`.

**Detect (v1, PR #56/#57):**

- Retries run in CI only (`--reruns=1`), and only for infra-shaped failures
  (`--only-rerun` regex); assertion failures never retry. Local runs never
  retry (`--reruns=0`).
- Every pass-on-retry is reported loudly (`utils/flaky_summary.py`) in the
  terminal and the GitHub step summary — a retry is an observability
  mechanism, not a fix.

**Contain / Remember / Decide (v2):**

- `@pytest.mark.quarantine(reason, expires)` converts to
  `xfail(strict=False)` at collection (`utils/quarantine.py`): a quarantined
  test keeps running and producing signal but never blocks a merge. An
  expired marker aborts the run with `UsageError` — fix or extend, never
  silent decay; expiries within 7 days are pre-announced in the candidates
  report.
- Every CI run's per-test outcomes are recorded
  (`utils/run_record.py`) and merged into a durable history on the
  `gh-pages` branch by `scripts/analyze_flake_history.py`, which runs inside
  the existing single-writer `publish-report` job (main-branch pushes only).
- The analyzer applies thresholds (≥2 fresh flake incidents in 30 runs, or
  fail rate ≥5% over ≥10 runs; release after 10 consecutive XPASS) and
  writes `candidates.md` — it proposes quarantine/un-quarantine candidates.
  A human applies every marker change via a reviewed PR; no bot edits test
  code.

## Consequences

- A red build means something real: infra noise is retried once and
  reported, known flakes are shielded by quarantine, and everything else is
  a genuine failure.
- The quarantine list is the set of markers in test files —
  `git grep quarantine` enumerates it; there is no separate registry.
- Flake statistics live in git (gh-pages), auditable via `git log`, with
  zero new services or databases.
- Engineers follow a pull-based ritual: check the step summary per run,
  review `candidates.md` weekly, act via marker PRs; the only hard stop is
  an expired quarantine.
- The marker is whole-test while detection is per-browser — quarantining a
  test flaky on one browser also unblocks the others (accepted trade-off;
  the report shows the per-browser contrast on every review).
