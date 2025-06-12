#!/bin/bash
# Quick PR review script for Neovim

PR_NUMBER=${1:-24}

echo "🔍 Reviewing PR #$PR_NUMBER"

# Fetch PR info
gh pr view $PR_NUMBER

# Show files changed
echo -e "\n📁 Files changed:"
gh pr diff $PR_NUMBER --name-only

# Option to checkout
echo -e "\n💡 To review in Neovim:"
echo "   1. Checkout: gh pr checkout $PR_NUMBER"
echo "   2. In Neovim: :Octo pr checkout $PR_NUMBER"
echo "   3. View diff: :DiffviewOpen origin/main...HEAD"
echo "   4. Or use: :Octo pr diff"

# Option to view diff in terminal
echo -e "\n📋 View diff now? (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    gh pr diff $PR_NUMBER | less
fi