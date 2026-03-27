#!/usr/bin/env python3
import json
import sys

VAGUE_PHRASES = [
    "fix it",
    "make it work",
    "just fix",
    "fix this",
    "make this work",
    "make it better",
    "clean it up",
    "rewrite it",
    "update it",
    "just do it",
]

STOP_REASON = """Prompt is too vague. Add context so Claude can act precisely.

  Vague:  "fix it"
  Better: "test_login in tests/auth/test_login.py fails with NoSuchElementError
           on #password. The selector changed after the latest UI update — update
           the locator to match the new HTML."

Include:
  1. Which file / function / test is affected
  2. What behaviour you expect
  3. What is currently happening (error, wrong output, etc.)"""


def main() -> None:
    """UserPromptSubmit hook: blocks vague prompts and asks for more context."""
    data = json.load(sys.stdin)
    prompt = data.get("prompt", "").strip().lower()
    word_count = len(prompt.split())

    if word_count < 20 and any(phrase in prompt for phrase in VAGUE_PHRASES):
        print(json.dumps({"continue": False, "stopReason": STOP_REASON}))


if __name__ == "__main__":
    main()
