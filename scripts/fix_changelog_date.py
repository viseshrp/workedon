#!/usr/bin/env python3
"""
Fix the release date for a given version in CHANGELOG.md,
by replacing '<Unreleased>' with today's date.
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
    target_line = f"## [{version}] - <Unreleased>"
    replacement_line = f"## [{version}] - {today}"

    lines = CHANGELOG_PATH.read_text(encoding="utf-8").splitlines()
    replaced = False

    new_lines = []
    for i, line in enumerate(lines):
        if line.strip() == target_line:
            print(f"🔍 Found line {i + 1}: {target_line}")
            new_lines.append(replacement_line)
            replaced = True
        else:
            new_lines.append(line)

    if not replaced:
        print(f"❌ ERROR: Could not find line exactly matching:\n   {target_line}")
        print("🔎 Tip: Double-check your changelog formatting.")
        sys.exit(1)

    CHANGELOG_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print("✅ Successfully updated changelog:")
    print(f"   {target_line} → {replacement_line}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/fix_changelog_date.py <version>")
        sys.exit(1)

    main(sys.argv[1])
