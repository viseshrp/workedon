#!/usr/bin/env bash

set -euo pipefail

VERSION=$(hatch version | sed 's/\.dev.*//')
echo "🏷 Releasing version: $VERSION"

# Update changelog date for this version
uv run python scripts/fix_changelog_date.py "$VERSION"

# Only commit if the changelog was actually updated
if ! git diff --quiet --exit-code CHANGELOG.md; then
  echo "✅ CHANGELOG.md updated, committing..."
  git add CHANGELOG.md
  git commit -m "📄 Update changelog for v$VERSION"
else
  echo "ℹ️ No changes to CHANGELOG.md. Skipping commit."
fi

# Always tag and push (tagging the latest HEAD whether or not changelog changed)
git tag "v$VERSION" -m "Release v$VERSION"
git push origin "v$VERSION"
