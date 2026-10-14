"""PostToolUse hook: lint and type-check right after Claude edits a file.

Runs `ruff check app tests` and `mypy app`. If either fails, the output goes to
stderr and we exit 2, which Claude Code feeds back to Claude so it fixes the
problem straight away (per-edit CI, in effect).

Settings run this with the project's .venv Python, and the tools are invoked as
`python -m ruff` / `python -m mypy`, so they're found without being on PATH.
A tool that isn't installed is skipped, not reported as a failure: a crashing
hook looks like a code problem and Claude would waste turns "fixing" it.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
CHECKS = [
    ("ruff", ["check", "app", "tests"]),
    ("mypy", ["app"]),
]


def edited_python(tool_call: dict) -> bool:
    """Only Python or tool-config edits can change ruff/mypy results."""
    path = tool_call.get("tool_input", {}).get("file_path", "")
    return path.endswith((".py", "pyproject.toml"))


def main() -> int:
    if not edited_python(json.load(sys.stdin)):
        return 0

    failures, skipped = [], []
    for tool, args in CHECKS:
        command = [sys.executable, "-m", tool, *args]
        result = subprocess.run(
            command, capture_output=True, text=True, cwd=PROJECT_DIR, timeout=120
        )
        output = f"{result.stdout}{result.stderr}".rstrip()
        if result.returncode != 0 and f"No module named {tool}" in output:
            skipped.append(tool)
        elif result.returncode != 0:
            failures.append(f"$ {tool} {' '.join(args)}\n{output}")

    if skipped:
        # stdout, not stderr: informational only, never blocks.
        print(f"[checks] skipped (not installed): {', '.join(skipped)}")
    if failures:
        print("\n\n".join(failures), file=sys.stderr)
        return 2  # exit 2 -> Claude sees stderr and can fix it
    return 0


if __name__ == "__main__":
    sys.exit(main())
