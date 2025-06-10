#!/usr/bin/env python3
"""
Fix the release date for a given version in CHANGELOG.md,
by replacing '[Unreleased]' with today's date.
"""

from datetime import date
from pathlib import Path
import sys

CHANGELOG_PATH = Path("CHANGELOG.md")


def main(version: str) -> None:
    if not CHANGELOG_PATH.exists():
        sys.exit(1)

    today = date.today().isoformat()
    target_line = f"## [{version}] - [Unreleased]"
    replacement_line = f"## [{version}] - {today}"

    lines = CHANGELOG_PATH.read_text(encoding="utf-8").splitlines()
    replaced = False

    new_lines = []
    for line in lines:
        if line.strip() == target_line:
            new_lines.append(replacement_line)
            replaced = True
        else:
            new_lines.append(line)

    if not replaced:
        sys.exit(1)

    CHANGELOG_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)

    main(sys.argv[1])
