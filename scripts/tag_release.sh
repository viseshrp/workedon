#!/usr/bin/env bash

set -euo pipefail

VERSION=$(hatch version | sed 's/\.dev.*//')
echo "🏷 Releasing version: $VERSION"

# Update changelog date for this version
python scripts/fix_changelog_date.py "$VERSION"

# Stage and commit changelog update
git add CHANGELOG.md
git commit -m "📄 Update changelog for v$VERSION"

# Create and push tag
git tag "v$VERSION" -m "Release v$VERSION"
git push origin "v$VERSION"
