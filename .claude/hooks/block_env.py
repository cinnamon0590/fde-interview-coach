"""PreToolUse hook: stop Claude Code from reading the .env file.

Claude Code pipes the pending tool call to this script as JSON on stdin.
Exit code 2 blocks the call, and whatever we print to stderr is shown to
Claude as the reason. Exit code 0 lets the call go ahead.
"""
from __future__ import annotations

import json
import sys

ALLOWED = ".env.example"  # the template has no secrets, so it stays readable


def main() -> int:
    tool_call = json.load(sys.stdin)
    file_path = tool_call.get("tool_input", {}).get("file_path", "")
    if ".env" in file_path and ALLOWED not in file_path:
        print(f"Blocked: {file_path} may contain secrets (API keys).", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
