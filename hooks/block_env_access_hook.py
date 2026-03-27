#!/usr/bin/env python3
import json
import re
import sys

# Matches .env as a path component: .env, /path/.env, .env.local — not .envrc
_ENV_PATH_RE = re.compile(r"(^|/)\.env\b")
# Matches .env as a standalone token in a command — not .envrc, not part of a longer word
_ENV_TOKEN_RE = re.compile(r"(?<![.\w/])\.env\b")


def _strip_heredocs(command: str) -> str:
    """Remove heredoc content to avoid false positives on documentation strings."""
    return re.sub(r"<<\s*-?\s*'?\w+'?.*", "", command, flags=re.DOTALL)


def main() -> None:
    """PreToolUse hook: blocks tool calls that reference .env files."""
    tool_args = json.load(sys.stdin)
    tool_input = tool_args.get("tool_input", {})

    read_path = tool_input.get("file_path") or tool_input.get("path") or ""
    bash_command = tool_input.get("command", "")

    if _ENV_PATH_RE.search(read_path):
        print("You cannot read the .env file", file=sys.stderr)
        sys.exit(2)

    if _ENV_TOKEN_RE.search(_strip_heredocs(bash_command)):
        print("You cannot read the .env file", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
