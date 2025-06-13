#!/usr/bin/env bash
set -euo pipefail

VERSION=$(hatch version | sed 's/\.dev.*//')
echo "🏷 Releasing version: $VERSION"

# Update changelog date for this version
uv run python scripts/check_changelog_date.py "$VERSION"

# Assert we're on main and clean
branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$branch" != "main" ]]; then
  echo "❌ ERROR: Must be on main branch to tag a release."
  exit 1
fi

if ! git diff --quiet HEAD; then
  echo "❌ ERROR: Working directory is dirty. Commit your changes through a PR."
  exit 1
fi

# Create and push tag only
git tag "v$VERSION" -m "Release v$VERSION"
git push origin "v$VERSION"
echo "✅ Tag v$VERSION pushed successfully."
