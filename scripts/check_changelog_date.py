#!/usr/bin/env python3
"""
Check release date for a given version in CHANGELOG.md.
"""

from datetime import date
from pathlib import Path
import sys

CHANGELOG_PATH = Path("CHANGELOG.md")


def main(version: str) -> None:
    if not CHANGELOG_PATH.exists():
        print(f"❌ ERROR: {CHANGELOG_PATH} does not exist.")
        sys.exit(1)

    today = date.today().isoformat()
    target_line = f"## [{version}] - {today}"

    found = False
    lines = CHANGELOG_PATH.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines):
        if line.strip() == target_line:
            print(f"🔍 Found line {i + 1}: {target_line}")
            found = True
            break

    if not found:
        print("❌ ERROR: CHANGELOG.md is not ready for release.")
        print(f"   Expected line: {target_line}")
        print("Tip: Check if it's still marked as '[Unreleased]' and update it to today's date.")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/check_changelog_date.py <version>")
        sys.exit(1)

    main(sys.argv[1])
