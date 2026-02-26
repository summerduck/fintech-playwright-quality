#!/usr/bin/env python3
"""Interactive utility to select and open test log files."""

import subprocess  # nosec B404
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from simple_term_menu import TerminalMenu


def get_file_mtime(log_path: Path) -> tuple[Path, datetime]:
    """Get modification time for a log file."""
    try:
        mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
        return (log_path, mtime)
    except (OSError, FileNotFoundError):
        return (log_path, datetime.min)


def find_all_logs() -> list[tuple[Path, datetime]]:
    """Find all .log files with their modification times."""
    search_dirs = ["test-logs"]
    log_paths: list[Path] = []

    # Use rglob for faster recursive search
    for search_dir in search_dirs:
        search_path = Path(search_dir)
        if search_path.exists():
            log_paths.extend(search_path.rglob("*.log"))

    # Get modification times in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        logs = list(executor.map(get_file_mtime, log_paths))

    # Sort by modification time (newest first)
    logs.sort(key=lambda x: x[1], reverse=True)
    return logs


def format_log_name(log_path: Path) -> str:
    """Extract test name from the log file path."""
    # Get filename without extension
    name = log_path.stem

    return name.replace("test_", "")


def open_log_file(log_path: Path) -> None:
    """Open log file in a new tab in the current Cursor window."""
    try:
        abs_path = log_path.resolve()
        # Open file in a new tab in the current Cursor window
        subprocess.run(["cursor", "--reuse-window", str(abs_path)], check=False)  # nosec B603 B607
    except FileNotFoundError:
        print("Error: 'cursor' command not found. Please install Cursor CLI tools.")
        sys.exit(1)


def main() -> None:
    """Main function to open log files in a new tab in the current Cursor window."""
    logs = find_all_logs()

    if not logs:
        print("No log files found in test-logs directory")
        sys.exit(1)

    # Build menu items with time and test name
    menu_items = []
    for log_path, mtime in logs:
        name = format_log_name(log_path)
        time_str = mtime.strftime("%H:%M:%S")
        # Show relative path if in subdirectory
        if log_path.parent.name == "failed_tests":
            menu_items.append(f"{time_str}  [FAILED] {name}")
        else:
            menu_items.append(f"{time_str}  {name}")

    # Create interactive menu
    terminal_menu = TerminalMenu(
        menu_items,
        title=f"Select log ({len(logs)} found) — type to search:",
        menu_cursor="❯ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("fg_cyan", "bold"),
        search_key=None,
        search_highlight_style=("fg_yellow", "bold"),
        cycle_cursor=True,
        clear_screen=True,
    )

    try:
        selected_index = terminal_menu.show()

        if selected_index is None:
            print("\nCancelled.")
            sys.exit(0)

        selected_log = logs[selected_index][0]
        print("\nOpening log...")
        open_log_file(selected_log)

    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
