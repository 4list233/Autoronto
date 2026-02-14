#!/bin/bash
# URGENT: Remove exposed API token from git history
# This script will rewrite git history to remove the hardcoded API token

set -e

echo "🚨 URGENT: Removing exposed API token from git history"
echo "========================================================"
echo ""
echo "⚠️  WARNING: This will rewrite git history!"
echo "    If you've already pushed to a remote, you'll need to force push."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "Step 1: Creating backup branch..."
git branch backup-before-token-removal 2>/dev/null || echo "  (backup branch already exists)"

echo ""
echo "Step 2: Removing token from git history..."
echo "  This may take a moment..."

# Use git filter-branch to remove the token from ALL commits
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch scripts/populate_test_project_hours.py' \
  --prune-empty --tag-name-filter cat -- --all

echo ""
echo "Step 3: Cleaning up..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "✅ Token removed from git history!"
echo ""
echo "Next steps:"
echo "  1. The file has been removed from ALL commits in history"
echo "  2. Add the cleaned file back (with .env support):"
echo "     git add scripts/populate_test_project_hours.py"
echo "     git commit -m \"Add populate script with .env support (token removed)\""
echo ""
echo "  3. If you've already pushed to remote:"
echo "     git push --force-with-lease origin main"
echo ""
echo "  4. ⚠️  IMPORTANT: Rotate your API token immediately!"
echo "     - Log into TeamGantt"
echo "     - Go to Settings → API"
echo "     - Generate a NEW token"
echo "     - Update your .env file"
echo ""
echo "  5. If you have a backup branch:"
echo "     git branch -D backup-before-token-removal"
echo ""
