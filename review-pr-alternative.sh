#!/bin/bash
# Alternative PR review methods

PR_NUMBER=${1:-24}

echo "🔍 Alternative ways to review PR #$PR_NUMBER"
echo ""
echo "1. Using Git + Diffview in Neovim:"
echo "   gh pr checkout $PR_NUMBER"
echo "   nvim"
echo "   :DiffviewOpen origin/main...HEAD"
echo ""
echo "2. Using plain git diff:"
echo "   git fetch origin pull/$PR_NUMBER/head:pr-$PR_NUMBER"
echo "   git diff main...pr-$PR_NUMBER"
echo ""
echo "3. Using GitHub CLI in terminal:"
echo "   gh pr diff $PR_NUMBER --color always | less -R"
echo ""
echo "4. View specific files:"
gh pr diff $PR_NUMBER --name-only | while read -r file; do
    echo "   nvim -d main:$file HEAD:$file"
done | head -5
echo ""
echo "5. Quick terminal review (press q to exit):"
echo "   Press Enter to view diff in terminal..."
read -r

gh pr diff $PR_NUMBER --color always | less -R