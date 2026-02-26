#!/usr/bin/env python3
"""Interactive utility to select and open Playwright trace files."""

import subprocess  # nosec B404
import sys
from datetime import datetime
from pathlib import Path

from simple_term_menu import TerminalMenu


def find_all_traces() -> list[tuple[Path, datetime]]:
    """Find all trace.zip files with their modification times."""
    search_dirs = ["test-results"]
    traces = []

    for search_dir in search_dirs:
        search_path = Path(search_dir)
        if search_path.exists():
            for root, _dirs, files in search_path.walk():
                if "trace.zip" in files:
                    trace_path = Path(root) / "trace.zip"
                    try:
                        mtime = datetime.fromtimestamp(trace_path.stat().st_mtime)
                    except (OSError, FileNotFoundError):
                        mtime = datetime.min
                    traces.append((trace_path, mtime))

    # Sort by modification time (newest first)
    traces.sort(key=lambda x: x[1], reverse=True)
    return traces


def format_trace_name(trace_path: Path) -> str:
    """Extract test details from the trace directory path.

    Directory pattern: tests-<app>-<classname>-test-<testname>-<browser>[-params]
    Return format:  tests-<app> > <classname> > test-<testname>-<browser>[-params]
    """
    parent = trace_path.parent.name

    if "-test-" not in parent:
        return parent

    parts = parent.split("-test-")
    if len(parts) < 3 or not parts[-1]:
        return parent

    app_part = parts[0]
    test_suffix = parts[-1]

    middle = "-test-".join(parts[1:-1])
    py_segments = middle.split("-py-")
    class_name = py_segments[-1] if len(py_segments) > 1 else middle

    return f"{app_part} > {class_name} > test-{test_suffix}"


def main() -> None:
    """Main function to open trace files in a new tab in the current Cursor window."""
    traces = find_all_traces()

    if not traces:
        print("No trace files found in test-results directory")
        sys.exit(1)

    # Build menu items with time and test name
    menu_items = []
    for trace_path, mtime in traces:
        name = format_trace_name(trace_path)
        time_str = mtime.strftime("%H:%M:%S")
        menu_items.append(f"{time_str}  {name}")

    # Create interactive menu
    terminal_menu = TerminalMenu(
        menu_items,
        title=f"Select trace ({len(traces)} found):",
        menu_cursor="❯ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("fg_cyan", "bold"),
        cycle_cursor=True,
        clear_screen=True,
    )

    try:
        selected_index = terminal_menu.show()

        if selected_index is None:
            print("\nCancelled.")
            sys.exit(0)

        selected_trace = traces[selected_index][0]
        print("\nOpening trace...")
        try:
            subprocess.run(  # nosec B603 B607
                ["playwright", "show-trace", str(selected_trace)], check=False
            )
        except FileNotFoundError:
            print("Error: 'playwright' command not found. Run: pip install playwright")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
