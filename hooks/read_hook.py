#!/usr/bin/env python3
import json
import sys


def main() -> None:
    """Read hook for Claude."""
    tool_args = json.load(sys.stdin)

    read_path = (
        tool_args.get("tool_input", {}).get("file_path")
        or tool_args.get("tool_input", {}).get("path")
        or ""
    )

    if ".env" in read_path:
        print("You cannot read the .env file", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
