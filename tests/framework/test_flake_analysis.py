"""Unit tests for the flake-history analyzer's threshold logic.

Plain in-memory tests over the pure functions of
``scripts/analyze_flake_history.py`` — no pytester, no CI, no filesystem
except where load_history's recovery behavior is the subject.
"""

import datetime as dt
import json
from pathlib import Path
from typing import Any

import pytest

from scripts.analyze_flake_history import (
    KEEP_RUNS,
    Report,
    detect,
    load_history,
    main,
    merge,
    render_markdown,
)

NODEID = "tests/app/test_x.py::test_y"
TODAY = dt.date(2026, 7, 9)


def _run(run_id: int, outcome: str = "passed", reruns: int = 0) -> dict[str, Any]:
    return {
        "run_id": str(run_id),
        "sha": "abc1234",
        "outcome": outcome,
        "reruns": reruns,
        "quarantined": False,
    }


def _clean(count: int, start: int = 0) -> list[dict[str, Any]]:
    return [_run(i) for i in range(start, start + count)]


def _incident(run_id: int) -> dict[str, Any]:
    return _run(run_id, outcome="passed", reruns=1)


def _fail(run_id: int) -> dict[str, Any]:
    return _run(run_id, outcome="failed")


def _xpass(run_id: int) -> dict[str, Any]:
    entry = _run(run_id, outcome="xpassed")
    entry["quarantined"] = True
    return entry


def _xfail(run_id: int) -> dict[str, Any]:
    entry = _run(run_id, outcome="xfailed")
    entry["quarantined"] = True
    return entry


def _history(runs: list[dict[str, Any]], browser: str = "chromium") -> dict[str, Any]:
    return {"schema": 1, "tests": {NODEID: {browser: runs}}}


def _two_browser_history(
    chromium: list[dict[str, Any]], firefox: list[dict[str, Any]]
) -> dict[str, Any]:
    return {"schema": 1, "tests": {NODEID: {"chromium": chromium, "firefox": firefox}}}


def _record(
    run_id: int, tests: list[dict[str, Any]], browser: str = "chromium"
) -> dict[str, Any]:
    return {
        "schema": 1,
        "run_id": str(run_id),
        "sha": "abc1234",
        "branch": "main",
        "browser": browser,
        "timestamp": "2026-07-09T12:00:00Z",
        "tests": tests,
    }


def _record_test(outcome: str = "passed", reruns: int = 0) -> dict[str, Any]:
    return {
        "nodeid": NODEID,
        "outcome": outcome,
        "reruns": reruns,
        "quarantined": False,
    }


# ── quarantine candidates ────────────────────────────────────────────────────


def test_two_recent_incidents_propose_quarantine() -> None:
    history = _history(_clean(8) + [_incident(8), _incident(9)])
    report = detect(history, {}, TODAY)
    assert NODEID in report.quarantine


def test_single_incident_is_not_enough() -> None:
    history = _history(_clean(9) + [_incident(9)])
    report = detect(history, {}, TODAY)
    assert report.quarantine == {}


def test_stale_incidents_self_clean() -> None:
    history = _history([_incident(0), _incident(1)] + _clean(15, start=2))
    report = detect(history, {}, TODAY)
    assert report.quarantine == {}


def test_fail_rate_branch_proposes() -> None:
    history = _history(_clean(9) + [_fail(9)] + _clean(9, start=10) + [_fail(19)])
    report = detect(history, {}, TODAY)
    assert NODEID in report.quarantine


def test_fail_rate_below_threshold_is_quiet() -> None:
    history = _history(_clean(29) + [_fail(29)])
    report = detect(history, {}, TODAY)
    assert report.quarantine == {}


def test_trailing_fail_streak_is_regression_not_flake() -> None:
    history = _history(_clean(10) + [_fail(10), _fail(11), _fail(12)])
    report = detect(history, {}, TODAY)
    assert report.quarantine == {}
    assert report.failing == {NODEID: ["chromium"]}


def test_currently_quarantined_test_is_never_proposed() -> None:
    history = _history(_clean(8) + [_incident(8), _incident(9)])
    report = detect(history, {NODEID: "2026-08-01"}, TODAY)
    assert report.quarantine == {}


# ── un-quarantine candidates ─────────────────────────────────────────────────


def test_release_after_ten_consecutive_xpass() -> None:
    history = _history([_xpass(i) for i in range(10)])
    report = detect(history, {NODEID: "2026-08-01"}, TODAY)
    assert report.release == [NODEID]


def test_release_needs_the_full_streak() -> None:
    history = _history([_xfail(0)] + [_xpass(i) for i in range(1, 10)])
    report = detect(history, {NODEID: "2026-08-01"}, TODAY)
    assert report.release == []


def test_release_requires_every_browser_clean() -> None:
    dirty = [_xpass(i) for i in range(9)] + [_xfail(9)]
    history = _two_browser_history([_xpass(i) for i in range(10)], dirty)
    report = detect(history, {NODEID: "2026-08-01"}, TODAY)
    assert report.release == []


# ── expiring markers ─────────────────────────────────────────────────────────


def test_marker_expiring_within_week_is_listed() -> None:
    history = _history([_xpass(0)])
    report = detect(history, {NODEID: "2026-07-12"}, TODAY)
    assert report.expiring == [(NODEID, "2026-07-12")]


def test_far_expiry_is_not_listed() -> None:
    history = _history([_xpass(0)])
    report = detect(history, {NODEID: "2026-09-01"}, TODAY)
    assert report.expiring == []


# ── merge ────────────────────────────────────────────────────────────────────


def test_merge_appends_new_run() -> None:
    history = _history(_clean(3))
    merge(history, [_record(99, [_record_test()])])
    runs = history["tests"][NODEID]["chromium"]
    assert len(runs) == 4
    assert runs[-1]["run_id"] == "99"


def test_merge_windows_to_keep_runs() -> None:
    history = _history(_clean(KEEP_RUNS))
    merge(history, [_record(999, [_record_test()])])
    runs = history["tests"][NODEID]["chromium"]
    assert len(runs) == KEEP_RUNS
    assert runs[-1]["run_id"] == "999"


def test_merge_is_idempotent_per_run_id() -> None:
    history = _history(_clean(3))
    record = _record(99, [_record_test()])
    merge(history, [record])
    merge(history, [record])
    assert len(history["tests"][NODEID]["chromium"]) == 4


# ── history loading / recovery ───────────────────────────────────────────────


def test_missing_history_starts_fresh(tmp_path: Path) -> None:
    history = load_history(tmp_path / "absent.json")
    assert history == {"schema": 1, "tests": {}}


def test_corrupt_history_starts_fresh(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    path.write_text("{not json")
    history = load_history(path)
    assert history == {"schema": 1, "tests": {}}


def test_schema_mismatch_starts_fresh(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    path.write_text(json.dumps({"schema": 99, "tests": {NODEID: {}}}))
    history = load_history(path)
    assert history == {"schema": 1, "tests": {}}


# ── rendering ────────────────────────────────────────────────────────────────


def test_healthy_report_says_so_explicitly() -> None:
    md = render_markdown(Report(), "owner/repo", TODAY, "Analyzed 0 run record(s)")
    assert "No candidates. Suite is healthy." in md


def test_candidate_includes_paste_ready_marker_with_computed_expiry() -> None:
    history = _history(_clean(8) + [_incident(8), _incident(9)])
    report = detect(history, {}, TODAY)
    md = render_markdown(report, "owner/repo", TODAY, "meta")
    assert '@pytest.mark.quarantine(reason="TICKET-???' in md
    assert 'expires="2026-08-08"' in md


def test_candidate_evidence_links_incident_runs() -> None:
    history = _history(_clean(8) + [_incident(8), _incident(9)])
    report = detect(history, {}, TODAY)
    md = render_markdown(report, "owner/repo", TODAY, "meta")
    assert "https://github.com/owner/repo/actions/runs/9" in md


def test_clean_browser_shown_alongside_dirty_one() -> None:
    dirty = _clean(8) + [_incident(8), _incident(9)]
    history = _two_browser_history(dirty, _clean(10))
    report = detect(history, {}, TODAY)
    md = render_markdown(report, "owner/repo", TODAY, "meta")
    assert "clean (10/10)" in md


def test_failing_not_flaky_section_renders() -> None:
    history = _history(_clean(10) + [_fail(10), _fail(11), _fail(12)])
    report = detect(history, {}, TODAY)
    md = render_markdown(report, "owner/repo", TODAY, "meta")
    assert "Failing, not flaky" in md
    assert "No candidates. Suite is healthy." not in md


def test_expiring_section_renders() -> None:
    history = _history([_xpass(0)])
    report = detect(history, {NODEID: "2026-07-12"}, TODAY)
    md = render_markdown(report, "owner/repo", TODAY, "meta")
    assert "Expiring soon" in md
    assert "2026-07-12" in md


# ── CLI end-to-end ───────────────────────────────────────────────────────────


def test_main_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    records_dir = tmp_path / "records"
    records_dir.mkdir()
    record = _record(99, [_record_test()])
    (records_dir / "run-record-chromium.json").write_text(json.dumps(record))
    out_dir = tmp_path / "publish"
    exit_code = main(
        [
            "--history-file",
            str(tmp_path / "gh-pages" / "flake-history" / "history.json"),
            "--run-records-dir",
            str(records_dir),
            "--output-dir",
            str(out_dir),
            "--repo",
            "owner/repo",
            "--browsers",
            "chromium,firefox,webkit",
        ]
    )
    assert exit_code == 0
    written = json.loads((out_dir / "history.json").read_text())
    assert NODEID in written["tests"]
    md = (out_dir / "candidates.md").read_text()
    assert "no run record for firefox" in md
    assert "no run record for webkit" in md
    assert capsys.readouterr().out == md
