"""Unit tests for log_helpers.clean_and_create_log_dirs()."""

from pathlib import Path
from typing import NamedTuple

import pytest

from utils import log_helpers
from utils.log_helpers import clean_and_create_log_dirs


class Dirs(NamedTuple):
    """Throwaway LOG_DIR / FAILED_LOG_DIR / ALLURE_RESULTS_DIR paths."""

    log_dir: Path
    failed_log_dir: Path
    allure_dir: Path


@pytest.fixture
def dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Dirs:
    """Point every dir-management module constant at a throwaway tmp_path tree.

    All three constants must be patched together: leaving any one of them
    unpatched means ``clean_and_create_log_dirs()`` would operate on the real
    project directory instead, which is both destructive and racy under
    xdist (other workers write to the real ``allure-results`` concurrently).
    """
    log_dir = tmp_path / "test-logs"
    failed_log_dir = log_dir / "failed_tests"
    allure_dir = tmp_path / "allure-results"
    monkeypatch.setattr(log_helpers, "LOG_DIR", log_dir)
    monkeypatch.setattr(log_helpers, "FAILED_LOG_DIR", failed_log_dir)
    monkeypatch.setattr(log_helpers, "ALLURE_RESULTS_DIR", allure_dir)
    return Dirs(log_dir, failed_log_dir, allure_dir)


@pytest.fixture
def stale_files_in_log_dir(dirs: Dirs) -> tuple[Path, Path]:
    """Populate LOG_DIR with a stale top-level file and a stale nested file."""
    dirs.log_dir.mkdir()
    stale_file = dirs.log_dir / "stale.log"
    stale_file.write_text("stale")
    dirs.failed_log_dir.mkdir()
    nested_file = dirs.failed_log_dir / "old.log"
    nested_file.write_text("old")
    return stale_file, nested_file


@pytest.fixture
def symlinked_dir_in_log_dir(dirs: Dirs, tmp_path: Path) -> tuple[Path, Path]:
    """Create LOG_DIR containing a symlink to an external target directory."""
    dirs.log_dir.mkdir()
    target_dir = tmp_path / "external_target_dir"
    target_dir.mkdir()
    keep_file = target_dir / "keep.txt"
    keep_file.write_text("keep")
    link = dirs.log_dir / "linked"
    link.symlink_to(target_dir, target_is_directory=True)
    return link, target_dir


@pytest.fixture
def symlinked_file_in_log_dir(dirs: Dirs, tmp_path: Path) -> tuple[Path, Path]:
    """Create LOG_DIR containing a symlink to an external target file."""
    dirs.log_dir.mkdir()
    target_file = tmp_path / "external_target.log"
    target_file.write_text("keep")
    link = dirs.log_dir / "linked.log"
    link.symlink_to(target_file)
    return link, target_file


@pytest.fixture
def stale_file_in_allure_results(dirs: Dirs) -> Path:
    """Populate ALLURE_RESULTS_DIR with a stale result file."""
    dirs.allure_dir.mkdir()
    stale_result = dirs.allure_dir / "result.json"
    stale_result.write_text("{}")
    return stale_result


@pytest.mark.unit
class TestCleanAndCreateLogDirs:
    """Verify clean_and_create_log_dirs() empties, protects symlinks, and recreates dirs."""

    def test_removes_regular_files_and_subdirs_from_log_dir(
        self, stale_files_in_log_dir: tuple[Path, Path]
    ) -> None:
        stale_file, nested_file = stale_files_in_log_dir
        clean_and_create_log_dirs()
        assert not stale_file.exists()
        assert not nested_file.exists()

    def test_unlinks_symlinked_dir_without_deleting_its_target(
        self, symlinked_dir_in_log_dir: tuple[Path, Path]
    ) -> None:
        link, target_dir = symlinked_dir_in_log_dir
        clean_and_create_log_dirs()
        assert not link.exists()
        assert target_dir.exists()

    def test_unlinks_symlinked_file_without_deleting_its_target(
        self, symlinked_file_in_log_dir: tuple[Path, Path]
    ) -> None:
        link, target_file = symlinked_file_in_log_dir
        clean_and_create_log_dirs()
        assert not link.exists()
        assert target_file.exists()

    def test_empties_allure_results_dir_contents_but_keeps_directory(
        self, stale_file_in_allure_results: Path, dirs: Dirs
    ) -> None:
        clean_and_create_log_dirs()
        assert dirs.allure_dir.is_dir()
        assert not stale_file_in_allure_results.exists()

    def test_creates_missing_log_and_allure_dirs(self, dirs: Dirs) -> None:
        clean_and_create_log_dirs()
        assert dirs.log_dir.is_dir()
        assert dirs.failed_log_dir.is_dir()
        assert dirs.allure_dir.is_dir()
