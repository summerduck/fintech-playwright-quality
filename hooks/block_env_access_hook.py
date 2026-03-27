#!/usr/bin/env python3
import json
import sys


def main() -> None:
    """Read hook for Claude."""
    tool_args = json.load(sys.stdin)

    tool_input = tool_args.get("tool_input", {})
    read_path = tool_input.get("file_path") or tool_input.get("path") or ""
    bash_command = tool_input.get("command", "")

    if ".env" in read_path or ".env" in bash_command:
        print("You cannot read the .env file", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
