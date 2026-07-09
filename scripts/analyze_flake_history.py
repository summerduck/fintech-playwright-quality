#!/usr/bin/env python3
"""Merge run records into flake history and propose (un-)quarantine candidates.

Runs in the ``publish-report`` CI job on main-branch pushes. Reads the
durable history from the gh-pages checkout, folds in the current run's
per-browser run records (written by ``utils/run_record.py``), applies the
detection thresholds from the v2 design spec, and writes two files into the
publish tree:

- ``history.json``  — updated durable history (last 50 runs per test/browser)
- ``candidates.md`` — human report: quarantine / un-quarantine candidates,
  expiring markers, deterministic failures, data gaps

The rendered markdown is also printed to stdout so the workflow can append
it to ``$GITHUB_STEP_SUMMARY``. The analyzer proposes; it never edits test
code and never fails the build (the workflow step uses continue-on-error).
Stdlib-only: it runs on the bare runner without installing dependencies.
"""

import datetime as dt
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA = 1
KEEP_RUNS = 50  # stored history window per (nodeid, browser)
DETECT_WINDOW = 30  # runs scanned for incidents / fail rate
FRESH_WINDOW = 10  # the most recent bad event must fall in this window
FAIL_STREAK = 3  # this many trailing fails = regression, not flake
MIN_RUNS_FOR_RATE = 10
FAIL_RATE_THRESHOLD = 0.05
RELEASE_STREAK = 10  # consecutive XPASS runs to propose un-quarantine
EXPIRY_WARN_DAYS = 7
QUARANTINE_TTL_DAYS = 30  # horizon for the ready-to-paste marker


@dataclass
class BrowserStats:
    """Detection inputs computed for one (nodeid, browser) history key."""

    browser: str
    total: int
    incidents: list[dict[str, Any]]
    fail_count: int
    fresh_bad: bool
    fail_streak: int
    release_streak_ok: bool


@dataclass
class Report:
    """Everything ``candidates.md`` needs, grouped by section."""

    quarantine: dict[str, list[BrowserStats]] = field(default_factory=dict)
    release: list[str] = field(default_factory=list)
    failing: dict[str, list[str]] = field(default_factory=dict)
    expiring: list[tuple[str, str]] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)


def _fresh_history() -> dict[str, Any]:
    return {"schema": SCHEMA, "tests": {}}


def load_history(path: Path) -> dict[str, Any]:
    """Load history; corrupt or schema-mismatched files start fresh (warn).

    History is derived data — the gh-pages git log retains old versions, so
    recovery by reset is safe and keeps the pipeline running.
    """
    if not path.exists():
        return _fresh_history()
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(f"warning: corrupt history at {path}; starting fresh", file=sys.stderr)
        return _fresh_history()
    if data.get("schema") != SCHEMA or not isinstance(data.get("tests"), dict):
        print(
            f"warning: unexpected history schema at {path}; starting fresh",
            file=sys.stderr,
        )
        return _fresh_history()
    return data


def load_run_records(records_dir: Path) -> list[dict[str, Any]]:
    """Load every readable run-record file; skip unreadable ones with a warning."""
    records: list[dict[str, Any]] = []
    for record_path in sorted(records_dir.glob("run-record-*.json")):
        try:
            record: dict[str, Any] = json.loads(record_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"warning: skipping corrupt {record_path}", file=sys.stderr)
            continue
        if record.get("schema") != SCHEMA:
            print(f"warning: skipping schema-mismatched {record_path}", file=sys.stderr)
            continue
        records.append(record)
    return records


def merge(history: dict[str, Any], records: list[dict[str, Any]]) -> None:
    """Fold run records into history, windowed to KEEP_RUNS per key.

    Idempotent per run_id: re-running the analyzer over the same artifacts
    (workflow re-run) must not duplicate entries.
    """
    for record in records:
        browser = record["browser"]
        for test in record["tests"]:
            runs: list[dict[str, Any]] = (
                history["tests"].setdefault(test["nodeid"], {}).setdefault(browser, [])
            )
            if any(run["run_id"] == record["run_id"] for run in runs):
                continue
            runs.append(
                {
                    "run_id": record["run_id"],
                    "sha": record["sha"],
                    "outcome": test["outcome"],
                    "reruns": test["reruns"],
                    "quarantined": test.get("quarantined", False),
                }
            )
            del runs[:-KEEP_RUNS]


def _is_incident(run: dict[str, Any]) -> bool:
    """v1's pass-on-retry: same commit failed then passed."""
    return bool(run["reruns"] > 0 and run["outcome"] == "passed")


def _is_bad(run: dict[str, Any]) -> bool:
    return _is_incident(run) or bool(run["outcome"] == "failed")


def analyze_runs(runs: list[dict[str, Any]], browser: str) -> BrowserStats:
    """Compute every detection input for one (nodeid, browser) key."""
    window = runs[-DETECT_WINDOW:]
    incidents = [run for run in window if _is_incident(run)]
    fail_count = sum(1 for run in window if run["outcome"] == "failed")
    fresh_bad = any(_is_bad(run) for run in runs[-FRESH_WINDOW:])
    fail_streak = 0
    for run in reversed(runs):
        if run["outcome"] != "failed":
            break
        fail_streak += 1
    tail = runs[-RELEASE_STREAK:]
    release_streak_ok = len(tail) == RELEASE_STREAK and all(
        run["outcome"] == "xpassed" and run["reruns"] == 0 for run in tail
    )
    return BrowserStats(
        browser=browser,
        total=len(window),
        incidents=incidents,
        fail_count=fail_count,
        fresh_bad=fresh_bad,
        fail_streak=fail_streak,
        release_streak_ok=release_streak_ok,
    )


def _is_quarantine_trigger(stats: BrowserStats) -> bool:
    """Spec thresholds: (≥2 incidents OR fail rate ≥5% over ≥10 runs),
    fresh, and not a deterministic regression."""
    if not stats.fresh_bad or stats.fail_streak >= FAIL_STREAK:
        return False
    if len(stats.incidents) >= 2:
        return True
    return (
        stats.total >= MIN_RUNS_FOR_RATE
        and stats.fail_count / stats.total >= FAIL_RATE_THRESHOLD
    )


def detect(
    history: dict[str, Any], quarantined_now: dict[str, str], today: dt.date
) -> Report:
    """Apply thresholds per (nodeid, browser); aggregate whole-test verdicts.

    ``quarantined_now`` maps nodeid -> expires for tests quarantined in the
    freshest run records (the marker is whole-test, so quarantine state and
    release decisions are whole-test too; evidence stays per-browser).
    """
    report = Report()
    for nodeid in sorted(history["tests"]):
        browsers = history["tests"][nodeid]
        stats = [
            analyze_runs(runs, browser) for browser, runs in sorted(browsers.items())
        ]
        failing_browsers = [s.browser for s in stats if s.fail_streak >= FAIL_STREAK]
        if failing_browsers:
            report.failing[nodeid] = failing_browsers
        if nodeid in quarantined_now:
            if stats and all(s.release_streak_ok for s in stats):
                report.release.append(nodeid)
        elif any(_is_quarantine_trigger(s) for s in stats):
            report.quarantine[nodeid] = stats
    warn_horizon = today + dt.timedelta(days=EXPIRY_WARN_DAYS)
    for nodeid, expires_raw in sorted(quarantined_now.items()):
        if dt.date.fromisoformat(expires_raw) <= warn_horizon:
            report.expiring.append((nodeid, expires_raw))
    return report
