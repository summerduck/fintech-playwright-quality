"""Logging helper functions and constants for the test infrastructure.

Provides directory management, filename building, and nodeid sanitisation
used by the per-test logging hooks in conftest.py.
"""

import os
import re
import shutil
from pathlib import Path

# ── Directory layout for test artifacts ──────────────────────────────────────
LOG_DIR = Path("test-logs")
FAILED_LOG_DIR = LOG_DIR / "failed_tests"
ALLURE_RESULTS_DIR = Path("allure-results")


def _empty_dir_contents(path: Path) -> None:
    """Remove everything inside ``path`` without removing ``path`` itself.

    Symlinks (whether they point at a file or a directory) are ``unlink()``-ed
    rather than followed, since ``shutil.rmtree`` on a symlinked directory
    would delete the *target's* contents instead of just the link.
    """
    if not path.exists():
        return

    for child in path.iterdir():
        if child.is_symlink():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def clean_and_create_log_dirs() -> None:
    """Empty the log tree and allure results, then recreate all required directories.

    Clears the *contents* of ``LOG_DIR`` and ``ALLURE_RESULTS_DIR`` rather than
    removing the directories themselves, since both may be bind-mounted Docker
    volumes — removing a mount point raises ``OSError: Device or resource busy``.
    """
    _empty_dir_contents(LOG_DIR)
    _empty_dir_contents(ALLURE_RESULTS_DIR)

    LOG_DIR.mkdir(exist_ok=True)
    FAILED_LOG_DIR.mkdir(parents=True, exist_ok=True)
    ALLURE_RESULTS_DIR.mkdir(exist_ok=True)


def ensure_log_dirs_exist() -> None:
    """Create log directories if they don't exist (safe for xdist workers)."""
    LOG_DIR.mkdir(exist_ok=True)
    FAILED_LOG_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_nodeid(node_id: str) -> str:
    """Clean up a pytest nodeid into a filesystem-safe path segment."""
    tokens = node_id.split("::")
    tokens[-1] = tokens[-1].replace("/", "-")
    tokens[-1] = re.sub(r"-+", "-", tokens[-1])
    node_id = "/".join([x for x in tokens if x != "()"])
    return re.sub(r"\[(.+)\]", r"-\1", node_id)


def get_last_element(node_id: str) -> str:
    """Extract the test name (last segment) from a sanitized nodeid."""
    return node_id.rsplit("/", maxsplit=1)[-1]


def build_log_filename(test_name: str) -> str:
    """Build a log filename, prefixed with the xdist worker ID when running in parallel."""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "")
    prefix = f"{worker_id}_" if worker_id else ""
    max_filename_length = 255  # NAME_MAX on macOS/Linux (filename only, not path)
    max_name_length = max_filename_length - len(prefix) - len(".log")
    truncated_test_name = test_name[:max_name_length]
    return f"{prefix}{truncated_test_name}.log"
